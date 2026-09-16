from decimal import Decimal
from uuid import uuid7

import pytest
from shared.domain.errors import ValidationError
from shared.domain.pagination import PageParams

from saury_backend.catalog.application.dtos.sneaker import (
    CreateSneakerCommand,
    ListSneakersQuery,
    SneakerDTO,
    UpdateSneakerCommand,
    UploadSneakerImageCommand,
)
from saury_backend.catalog.application.use_cases.image import UploadSneakerImage
from saury_backend.catalog.application.use_cases.sneaker import (
    CreateSneaker,
    DeleteSneaker,
    GetSneaker,
    ListSneakers,
    UpdateSneaker,
)
from saury_backend.catalog.domain.errors import (
    BrandNotFound,
    CategoryNotFound,
    SneakerNotFound,
    SneakerSlugAlreadyExists,
)
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerSort
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus


def create_command(brand, category, **overrides) -> CreateSneakerCommand:
    values = {
        "name": "Air Max 90",
        "description": "Classic runner",
        "brand_id": brand.id,
        "category_id": category.id,
        "gender": "unisex",
        "price": Decimal("130"),
        "currency": "USD",
    }
    return CreateSneakerCommand(**(values | overrides))


@pytest.fixture
def create_sneaker(sneaker_repository, brand_repository, category_repository, unit_of_work) -> CreateSneaker:
    return CreateSneaker(sneaker_repository, brand_repository, category_repository, unit_of_work)


async def test_create_sneaker_starts_as_draft(create_sneaker, brand, category, unit_of_work) -> None:
    sneaker = await create_sneaker.execute(create_command(brand, category))

    assert sneaker.slug == "air-max-90"
    assert sneaker.status == "draft"
    assert sneaker.base_price.amount == Decimal("130.00")
    assert sneaker.base_price.currency == "USD"
    assert unit_of_work.commits == 1


async def test_create_sneaker_requires_existing_brand(create_sneaker, brand, category, unit_of_work) -> None:
    with pytest.raises(BrandNotFound):
        await create_sneaker.execute(create_command(brand, category, brand_id=uuid7()))
    assert unit_of_work.commits == 0


async def test_create_sneaker_requires_existing_category(create_sneaker, brand, category) -> None:
    with pytest.raises(CategoryNotFound):
        await create_sneaker.execute(create_command(brand, category, category_id=uuid7()))


async def test_create_sneaker_rejects_duplicated_slug(create_sneaker, brand, category) -> None:
    await create_sneaker.execute(create_command(brand, category))

    with pytest.raises(SneakerSlugAlreadyExists):
        await create_sneaker.execute(create_command(brand, category, name="AIR MAX 90"))


@pytest.mark.parametrize(
    "overrides",
    [{"price": Decimal("-1")}, {"currency": "usd"}, {"gender": "aliens"}, {"name": " "}],
    ids=["negative-price", "invalid-currency", "invalid-gender", "blank-name"],
)
async def test_create_sneaker_rejects_invalid_data(create_sneaker, brand, category, overrides) -> None:
    with pytest.raises(ValidationError):
        await create_sneaker.execute(create_command(brand, category, **overrides))


async def test_update_sneaker_changes_data(
    create_sneaker, sneaker_repository, brand_repository, category_repository, unit_of_work, brand, category
) -> None:
    created = await create_sneaker.execute(create_command(brand, category))

    updated = await UpdateSneaker(sneaker_repository, brand_repository, category_repository, unit_of_work).execute(
        UpdateSneakerCommand(
            sneaker_id=created.id,
            name="Air Max 95",
            description="",
            brand_id=brand.id,
            category_id=category.id,
            gender="men",
            price=Decimal("150"),
            currency="EUR",
        )
    )

    assert (updated.name, updated.slug, updated.gender) == ("Air Max 95", "air-max-95", "men")
    assert await GetSneaker(sneaker_repository).execute(created.id) == updated


async def test_update_sneaker_raises_when_missing(
    sneaker_repository, brand_repository, category_repository, unit_of_work, brand, category
) -> None:
    with pytest.raises(SneakerNotFound):
        await UpdateSneaker(sneaker_repository, brand_repository, category_repository, unit_of_work).execute(
            UpdateSneakerCommand(uuid7(), "X", "", brand.id, category.id, "men", Decimal("1"), "USD")
        )


async def test_get_sneaker_raises_when_missing(sneaker_repository) -> None:
    with pytest.raises(SneakerNotFound):
        await GetSneaker(sneaker_repository).execute(uuid7())


async def test_list_sneakers_translates_query_into_filters(sneaker_repository, create_sneaker, brand, category) -> None:
    await create_sneaker.execute(create_command(brand, category))

    page = await ListSneakers(sneaker_repository).execute(
        ListSneakersQuery(
            brand="nike",
            gender="men",
            status="active",
            size=Decimal("42.5"),
            min_price=Decimal("50"),
            max_price=Decimal("200"),
            currency="EUR",
            in_stock=True,
            q=" max ",
            sort="price",
            descending=True,
        ),
        PageParams(),
    )

    assert [type(item) for item in page.items] == [SneakerDTO]
    filters = sneaker_repository.last_filters
    assert filters.brand.value == "nike"
    assert filters.gender is Gender.MEN
    assert filters.status is SneakerStatus.ACTIVE
    assert filters.size == ShoeSize.of("42.5")
    assert (str(filters.min_price), str(filters.max_price)) == ("50.00 EUR", "200.00 EUR")
    assert (filters.in_stock, filters.q, filters.sort, filters.descending) == (True, "max", SneakerSort.PRICE, True)


@pytest.mark.parametrize(
    "query",
    [
        ListSneakersQuery(min_price=Decimal("100")),
        ListSneakersQuery(max_price=Decimal("100")),
        ListSneakersQuery(sort="popularity"),
        ListSneakersQuery(status="deleted"),
        ListSneakersQuery(size=Decimal("42.3")),
    ],
    ids=["min-price-without-currency", "max-price-without-currency", "invalid-sort", "invalid-status", "invalid-size"],
)
async def test_list_sneakers_rejects_invalid_queries(sneaker_repository, query) -> None:
    with pytest.raises(ValidationError):
        await ListSneakers(sneaker_repository).execute(query, PageParams())


async def test_delete_sneaker_removes_aggregate_and_stored_images(
    create_sneaker, sneaker_repository, image_storage, unit_of_work, brand, category
) -> None:
    created = await create_sneaker.execute(create_command(brand, category))
    upload = UploadSneakerImage(sneaker_repository, image_storage, unit_of_work, "sauri-store/test")
    for name in ("front.png", "side.png"):
        await upload.execute(UploadSneakerImageCommand(created.id, b"png", name))

    await DeleteSneaker(sneaker_repository, image_storage, unit_of_work).execute(created.id)

    with pytest.raises(SneakerNotFound):
        await GetSneaker(sneaker_repository).execute(created.id)
    assert image_storage.images == {}
    assert len(image_storage.deleted) == 2


async def test_delete_sneaker_tolerates_storage_failures(
    create_sneaker, sneaker_repository, image_storage, unit_of_work, brand, category, caplog
) -> None:
    created = await create_sneaker.execute(create_command(brand, category))
    await UploadSneakerImage(sneaker_repository, image_storage, unit_of_work, "sauri-store/test").execute(
        UploadSneakerImageCommand(created.id, b"png", "front.png")
    )
    image_storage.fail_on_delete = True

    await DeleteSneaker(sneaker_repository, image_storage, unit_of_work).execute(created.id)

    assert await sneaker_repository.get(created.id) is None
    assert "Failed to delete stored image" in caplog.text
