import os
from collections.abc import AsyncIterator
from datetime import date
from pathlib import Path

import pytest
from shared.domain.money import Money
from shared.domain.pagination import PageParams
from shared.domain.slug import Slug
from shared.infrastructure.persistence.database import Base, create_engine, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession

from saury_backend.catalog.domain.entities.brand import Brand
from saury_backend.catalog.domain.entities.category import Category
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerFilters, SneakerSort
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.infrastructure.persistence.brand_repository import SqlAlchemyBrandRepository
from saury_backend.catalog.infrastructure.persistence.category_repository import SqlAlchemyCategoryRepository
from saury_backend.catalog.infrastructure.persistence.sneaker_repository import SqlAlchemySneakerRepository
from saury_backend.config.settings import to_async_database_url


@pytest.fixture
async def session(tmp_path: Path) -> AsyncIterator[AsyncSession]:
    configured_url = os.environ.get("TEST_DATABASE_URL")
    database_url = (
        to_async_database_url(configured_url)
        if configured_url
        else f"sqlite+aiosqlite:///{(tmp_path / 'catalog.db').as_posix()}"
    )
    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    async with create_session_factory(engine)() as db_session:
        yield db_session
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def repository(session: AsyncSession) -> SqlAlchemySneakerRepository:
    return SqlAlchemySneakerRepository(session)


@pytest.fixture
async def catalog(session: AsyncSession) -> dict[str, Brand | Category]:
    items: dict[str, Brand | Category] = {"nike": Brand.create("Nike"), "adidas": Brand.create("Adidas")}
    for brand in items.values():
        await SqlAlchemyBrandRepository(session).save(brand)
    running, lifestyle = Category.create("Running"), Category.create("Lifestyle")
    for category in (running, lifestyle):
        await SqlAlchemyCategoryRepository(session).save(category)
    await session.commit()
    return items | {"running": running, "lifestyle": lifestyle}


async def store(
    repository: SqlAlchemySneakerRepository,
    session: AsyncSession,
    name: str,
    brand: Brand | Category,
    category: Brand | Category,
    *,
    price: str = "100",
    currency: str = "USD",
    gender: Gender = Gender.UNISEX,
    description: str = "",
    release_date: date | None = None,
    sizes: dict[str, int] | None = None,
    publish: bool = False,
) -> Sneaker:
    sneaker = Sneaker.create(
        name, description, brand.id, category.id, gender, Money.of(price, currency), release_date=release_date
    )
    colorway = sneaker.add_colorway("Default", "#000000", Slug.from_text(name).value.upper())
    for size, stock in (sizes or {}).items():
        sneaker.set_size_stock(colorway.id, ShoeSize.of(size), stock)
    if publish:
        sneaker.set_size_stock(colorway.id, ShoeSize.of("40"), 1)
        sneaker.add_image(f"p/{sneaker.slug}", f"https://images.test/{sneaker.slug}")
        sneaker.publish()
    await repository.save(sneaker)
    await session.commit()
    return sneaker


async def names(repository: SqlAlchemySneakerRepository, filters: SneakerFilters) -> list[str]:
    page = await repository.paginate(filters, PageParams(size=100))
    return [sneaker.name for sneaker in page.items]


async def test_round_trips_the_whole_aggregate(repository, session, catalog) -> None:
    sneaker = Sneaker.create(
        "Air Max 90",
        "Classic runner",
        catalog["nike"].id,
        catalog["running"].id,
        Gender.MEN,
        Money.of("129.99", "EUR"),
        release_date=date(2026, 3, 26),
    )
    colorway = sneaker.add_colorway("Infrared", "#ff0000", "AM90-INF", Money.of("149.50", "EUR"))
    sneaker.set_size_stock(colorway.id, ShoeSize.of("42.5"), 4)
    sneaker.set_size_stock(colorway.id, ShoeSize.of("41"), 0)
    sneaker.add_image("p/front", "https://images.test/front", alt="Front")
    sneaker.add_image("p/side", "https://images.test/side")
    await repository.save(sneaker)
    await session.commit()
    session.expunge_all()

    loaded = await repository.get(sneaker.id)

    assert loaded is not None
    assert (loaded.name, loaded.slug, loaded.gender, loaded.status) == (
        "Air Max 90",
        Slug("air-max-90"),
        Gender.MEN,
        SneakerStatus.DRAFT,
    )
    assert loaded.base_price == Money.of("129.99", "EUR")
    assert loaded.release_date == date(2026, 3, 26)
    [loaded_colorway] = loaded.colorways
    assert loaded_colorway.price_override == Money.of("149.50", "EUR")
    assert [(str(size.size), size.stock) for size in loaded_colorway.sizes] == [("41", 0), ("42.5", 4)]
    assert [(image.alt, image.position, image.is_primary) for image in loaded.images] == [
        ("Front", 0, True),
        ("", 1, False),
    ]


async def test_save_updates_and_removes_children(repository, session, catalog) -> None:
    sneaker = await store(repository, session, "Samba", catalog["adidas"], catalog["lifestyle"], sizes={"42": 1})
    extra = sneaker.add_colorway("Gum", "#c19a6b", "SAMBA-GUM")
    first = sneaker.add_image("p/1", "https://images.test/1")
    second = sneaker.add_image("p/2", "https://images.test/2")
    await repository.save(sneaker)
    await session.commit()

    sneaker.remove_colorway(extra.id)
    sneaker.set_size_stock(sneaker.colorways[0].id, ShoeSize.of("42"), 9)
    sneaker.remove_image(first.id)
    await repository.save(sneaker)
    await session.commit()
    session.expunge_all()

    loaded = await repository.get(sneaker.id)
    assert [colorway.sku for colorway in loaded.colorways] == ["SAMBA"]
    assert loaded.colorways[0].sizes[0].stock == 9
    assert [(image.id, image.position, image.is_primary) for image in loaded.images] == [(second.id, 0, True)]


async def test_lookups_by_slug_sku_brand_and_category(repository, session, catalog) -> None:
    sneaker = await store(repository, session, "Gazelle", catalog["adidas"], catalog["lifestyle"])

    assert (await repository.get_by_slug(Slug("gazelle"))).id == sneaker.id
    assert await repository.find_sku_owner("GAZELLE") == sneaker.id
    assert await repository.find_sku_owner("UNKNOWN") is None
    assert await repository.exists_for_brand(catalog["adidas"].id)
    assert not await repository.exists_for_brand(catalog["nike"].id)
    assert await repository.exists_for_category(catalog["lifestyle"].id)
    assert not await repository.exists_for_category(catalog["running"].id)


async def test_delete_removes_aggregate(repository, session, catalog) -> None:
    sneaker = await store(repository, session, "Samba", catalog["adidas"], catalog["lifestyle"], sizes={"42": 1})

    await repository.delete(sneaker)
    await session.commit()

    assert await repository.get(sneaker.id) is None
    assert await repository.find_sku_owner("SAMBA") is None


async def test_filters_by_brand_size_and_stock(repository, session, catalog) -> None:
    nike, adidas, running = catalog["nike"], catalog["adidas"], catalog["running"]
    await store(repository, session, "Pegasus", nike, running, sizes={"42": 3})
    await store(repository, session, "Vomero", nike, running, sizes={"42": 0, "43": 2})
    await store(repository, session, "Invincible", nike, running, sizes={"44": 5})
    await store(repository, session, "Adizero", adidas, running, sizes={"42": 8})

    in_stock_42 = SneakerFilters(brand=Slug("nike"), size=ShoeSize.of("42"), in_stock=True)

    assert await names(repository, in_stock_42) == ["Pegasus"]
    assert await names(repository, SneakerFilters(brand=Slug("nike"), size=ShoeSize.of("42"))) == [
        "Pegasus",
        "Vomero",
    ]
    assert await names(repository, SneakerFilters(in_stock=True, sort=SneakerSort.NAME)) == [
        "Adizero",
        "Invincible",
        "Pegasus",
        "Vomero",
    ]


async def test_filters_by_category_gender_status_and_text(repository, session, catalog) -> None:
    nike, running, lifestyle = catalog["nike"], catalog["running"], catalog["lifestyle"]
    await store(repository, session, "Pegasus", nike, running, gender=Gender.MEN, description="Daily 100% trainer")
    await store(repository, session, "Cortez", nike, lifestyle, gender=Gender.WOMEN, publish=True)
    await store(repository, session, "Air Force 1", nike, lifestyle, description="Court_classic", publish=True)

    assert await names(repository, SneakerFilters(category=Slug("running"))) == ["Pegasus"]
    assert await names(repository, SneakerFilters(gender=Gender.WOMEN)) == ["Cortez"]
    assert await names(
        repository, SneakerFilters(status=SneakerStatus.ACTIVE, sort=SneakerSort.NAME)
    ) == ["Air Force 1", "Cortez"]
    assert await names(repository, SneakerFilters(q="PEGA")) == ["Pegasus"]
    assert await names(repository, SneakerFilters(q="100%")) == ["Pegasus"]
    assert await names(repository, SneakerFilters(q="y_1")) == []
    assert await names(repository, SneakerFilters(q="rt_c")) == ["Air Force 1"]


async def test_filters_and_sorts_by_price_within_currency(repository, session, catalog) -> None:
    nike, running = catalog["nike"], catalog["running"]
    await store(repository, session, "Cheap", nike, running, price="60")
    await store(repository, session, "Mid", nike, running, price="120.50")
    await store(repository, session, "Premium", nike, running, price="250")
    await store(repository, session, "Euro", nike, running, price="120.50", currency="EUR")

    usd_range = SneakerFilters(min_price=Money.of("100", "USD"), max_price=Money.of("250", "USD"))

    assert await names(repository, usd_range) == ["Mid", "Premium"]
    assert await names(repository, SneakerFilters(max_price=Money.of("200", "EUR"))) == ["Euro"]
    assert await names(repository, SneakerFilters(sort=SneakerSort.PRICE)) == ["Euro", "Cheap", "Mid", "Premium"]
    assert await names(repository, SneakerFilters(sort=SneakerSort.PRICE, descending=True)) == [
        "Premium",
        "Mid",
        "Cheap",
        "Euro",
    ]


async def test_sorts_by_release_date_with_missing_dates_last(repository, session, catalog) -> None:
    nike, running = catalog["nike"], catalog["running"]
    await store(repository, session, "Undated", nike, running)
    await store(repository, session, "Old", nike, running, release_date=date(2020, 1, 1))
    await store(repository, session, "New", nike, running, release_date=date(2026, 1, 1))

    assert await names(repository, SneakerFilters(sort=SneakerSort.RELEASE_DATE)) == ["Old", "New", "Undated"]
    assert await names(repository, SneakerFilters(sort=SneakerSort.RELEASE_DATE, descending=True)) == [
        "New",
        "Old",
        "Undated",
    ]


async def test_paginates_filtered_results(repository, session, catalog) -> None:
    for name in ("A1", "A2", "A3", "B1"):
        await store(repository, session, name, catalog["nike"], catalog["running"])

    page = await repository.paginate(SneakerFilters(q="a", sort=SneakerSort.NAME), PageParams(page=2, size=2))

    assert [sneaker.name for sneaker in page.items] == ["A3"]
    assert (page.total, page.pages) == (3, 2)
