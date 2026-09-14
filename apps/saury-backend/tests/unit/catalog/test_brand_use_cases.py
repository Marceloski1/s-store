from uuid import uuid7

import pytest
from shared.domain.errors import ValidationError
from shared.domain.pagination import PageParams

from saury_backend.catalog.application.dtos.brand import CreateBrandCommand, UpdateBrandCommand
from saury_backend.catalog.application.use_cases.brand import (
    CreateBrand,
    DeleteBrand,
    GetBrand,
    ListBrands,
    UpdateBrand,
)
from saury_backend.catalog.domain.errors import BrandNotFound, BrandSlugAlreadyExists


async def test_create_brand_generates_slug_from_name(brand_repository, unit_of_work) -> None:
    brand = await CreateBrand(brand_repository, unit_of_work).execute(CreateBrandCommand(name="  New Balance "))

    assert brand.name == "New Balance"
    assert brand.slug == "new-balance"
    assert unit_of_work.commits == 1


async def test_create_brand_uses_explicit_slug(brand_repository, unit_of_work) -> None:
    brand = await CreateBrand(brand_repository, unit_of_work).execute(CreateBrandCommand(name="Nike", slug="nike-inc"))

    assert brand.slug == "nike-inc"


async def test_create_brand_rejects_duplicated_slug(brand_repository, unit_of_work) -> None:
    create_brand = CreateBrand(brand_repository, unit_of_work)
    await create_brand.execute(CreateBrandCommand(name="Nike"))

    with pytest.raises(BrandSlugAlreadyExists):
        await create_brand.execute(CreateBrandCommand(name="NIKE"))

    assert unit_of_work.commits == 1


async def test_create_brand_rejects_blank_name(brand_repository, unit_of_work) -> None:
    with pytest.raises(ValidationError):
        await CreateBrand(brand_repository, unit_of_work).execute(CreateBrandCommand(name="   "))


async def test_get_brand_raises_when_missing(brand_repository) -> None:
    with pytest.raises(BrandNotFound):
        await GetBrand(brand_repository).execute(uuid7())


async def test_list_brands_returns_page_sorted_by_name(brand_repository, unit_of_work) -> None:
    create_brand = CreateBrand(brand_repository, unit_of_work)
    for name in ("Puma", "Adidas", "Nike"):
        await create_brand.execute(CreateBrandCommand(name=name))

    page = await ListBrands(brand_repository).execute(PageParams(page=1, size=2))

    assert [brand.name for brand in page.items] == ["Adidas", "Nike"]
    assert page.total == 3
    assert page.pages == 2


async def test_update_brand_changes_name_and_regenerates_slug(brand_repository, unit_of_work) -> None:
    created = await CreateBrand(brand_repository, unit_of_work).execute(CreateBrandCommand(name="Nike"))

    updated = await UpdateBrand(brand_repository, unit_of_work).execute(
        UpdateBrandCommand(brand_id=created.id, name="Nike SB")
    )

    assert updated.slug == "nike-sb"
    assert await GetBrand(brand_repository).execute(created.id) == updated


async def test_update_brand_keeps_its_own_slug(brand_repository, unit_of_work) -> None:
    created = await CreateBrand(brand_repository, unit_of_work).execute(CreateBrandCommand(name="Nike"))

    updated = await UpdateBrand(brand_repository, unit_of_work).execute(
        UpdateBrandCommand(brand_id=created.id, name="Nike", slug="nike")
    )

    assert updated == created


async def test_update_brand_rejects_slug_of_another_brand(brand_repository, unit_of_work) -> None:
    create_brand = CreateBrand(brand_repository, unit_of_work)
    await create_brand.execute(CreateBrandCommand(name="Nike"))
    adidas = await create_brand.execute(CreateBrandCommand(name="Adidas"))

    with pytest.raises(BrandSlugAlreadyExists):
        await UpdateBrand(brand_repository, unit_of_work).execute(
            UpdateBrandCommand(brand_id=adidas.id, name="Adidas", slug="nike")
        )

    assert await GetBrand(brand_repository).execute(adidas.id) == adidas


async def test_update_brand_raises_when_missing(brand_repository, unit_of_work) -> None:
    with pytest.raises(BrandNotFound):
        await UpdateBrand(brand_repository, unit_of_work).execute(UpdateBrandCommand(brand_id=uuid7(), name="Nike"))


async def test_delete_brand_removes_it(brand_repository, unit_of_work) -> None:
    created = await CreateBrand(brand_repository, unit_of_work).execute(CreateBrandCommand(name="Nike"))

    await DeleteBrand(brand_repository, unit_of_work).execute(created.id)

    with pytest.raises(BrandNotFound):
        await GetBrand(brand_repository).execute(created.id)
    assert unit_of_work.commits == 2


async def test_delete_brand_raises_when_missing(brand_repository, unit_of_work) -> None:
    with pytest.raises(BrandNotFound):
        await DeleteBrand(brand_repository, unit_of_work).execute(uuid7())
