from decimal import Decimal
from uuid import uuid7

import pytest
from shared.domain.errors import ValidationError
from shared.domain.money import Money

from saury_backend.catalog.application.dtos.sneaker import (
    CreateColorwayCommand,
    RemoveSizeCommand,
    SetSizeStockCommand,
    UpdateColorwayCommand,
)
from saury_backend.catalog.application.use_cases.colorway import CreateColorway, DeleteColorway, UpdateColorway
from saury_backend.catalog.application.use_cases.size_variant import RemoveSize, SetSizeStock
from saury_backend.catalog.application.use_cases.sneaker import GetSneaker
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.errors import ColorwayNotFound, SizeVariantNotFound, SkuAlreadyExists, SneakerNotFound
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize


async def store_sneaker(repository, name: str, currency: str = "USD") -> Sneaker:
    sneaker = Sneaker.create(name, "", uuid7(), uuid7(), Gender.UNISEX, Money.of("100", currency))
    await repository.save(sneaker)
    return sneaker


async def test_create_colorway_uses_sneaker_currency_for_override(sneaker_repository, unit_of_work) -> None:
    sneaker = await store_sneaker(sneaker_repository, "Samba", currency="EUR")

    result = await CreateColorway(sneaker_repository, unit_of_work).execute(
        CreateColorwayCommand(sneaker.id, "Gum", "#c19a6b", "samba-gum", Decimal("120"))
    )

    [colorway] = result.colorways
    assert colorway.sku == "SAMBA-GUM"
    assert (colorway.price_override.amount, colorway.price_override.currency) == (Decimal("120.00"), "EUR")
    assert colorway.effective_price.amount == Decimal("120.00")
    assert unit_of_work.commits == 1


async def test_sku_is_unique_across_sneakers(sneaker_repository, unit_of_work) -> None:
    samba = await store_sneaker(sneaker_repository, "Samba")
    gazelle = await store_sneaker(sneaker_repository, "Gazelle")
    create = CreateColorway(sneaker_repository, unit_of_work)
    await create.execute(CreateColorwayCommand(samba.id, "White", "#ffffff", "AD-001"))

    with pytest.raises(SkuAlreadyExists):
        await create.execute(CreateColorwayCommand(gazelle.id, "White", "#ffffff", "ad-001"))


async def test_update_colorway_keeps_own_sku_and_changes_fields(sneaker_repository, unit_of_work) -> None:
    sneaker = await store_sneaker(sneaker_repository, "Samba")
    created = await CreateColorway(sneaker_repository, unit_of_work).execute(
        CreateColorwayCommand(sneaker.id, "White", "#ffffff", "AD-001", Decimal("90"))
    )

    result = await UpdateColorway(sneaker_repository, unit_of_work).execute(
        UpdateColorwayCommand(sneaker.id, created.colorways[0].id, "Cloud White", "#fafafa", "AD-001")
    )

    [colorway] = result.colorways
    assert (colorway.name, colorway.color_code, colorway.price_override) == ("Cloud White", "#FAFAFA", None)
    assert colorway.effective_price.amount == Decimal("100.00")


async def test_delete_colorway(sneaker_repository, unit_of_work) -> None:
    sneaker = await store_sneaker(sneaker_repository, "Samba")
    created = await CreateColorway(sneaker_repository, unit_of_work).execute(
        CreateColorwayCommand(sneaker.id, "White", "#ffffff", "AD-001")
    )
    delete = DeleteColorway(sneaker_repository, unit_of_work)

    result = await delete.execute(sneaker.id, created.colorways[0].id)

    assert result.colorways == []
    with pytest.raises(ColorwayNotFound):
        await delete.execute(sneaker.id, created.colorways[0].id)


async def test_colorway_use_cases_require_existing_sneaker(sneaker_repository, unit_of_work) -> None:
    with pytest.raises(SneakerNotFound):
        await CreateColorway(sneaker_repository, unit_of_work).execute(
            CreateColorwayCommand(uuid7(), "White", "#ffffff", "AD-001")
        )


async def test_set_size_stock_adds_and_adjusts(sneaker_repository, unit_of_work) -> None:
    sneaker = await store_sneaker(sneaker_repository, "Samba")
    colorway = sneaker.add_colorway("White", "#ffffff", "AD-001")
    await sneaker_repository.save(sneaker)
    set_stock = SetSizeStock(sneaker_repository, unit_of_work)

    await set_stock.execute(SetSizeStockCommand(sneaker.id, colorway.id, Decimal("42"), 3))
    result = await set_stock.execute(SetSizeStockCommand(sneaker.id, colorway.id, Decimal("42"), 8))

    assert [(size.size, size.stock) for size in result.colorways[0].sizes] == [(Decimal("42.0"), 8)]


async def test_negative_stock_is_rejected_without_changes(sneaker_repository, unit_of_work) -> None:
    sneaker = await store_sneaker(sneaker_repository, "Samba")
    colorway = sneaker.add_colorway("White", "#ffffff", "AD-001")
    sneaker.set_size_stock(colorway.id, ShoeSize.of("42"), 5)
    await sneaker_repository.save(sneaker)

    with pytest.raises(ValidationError):
        await SetSizeStock(sneaker_repository, unit_of_work).execute(
            SetSizeStockCommand(sneaker.id, colorway.id, Decimal("42"), -1)
        )

    stored = await GetSneaker(sneaker_repository).execute(sneaker.id)
    assert stored.colorways[0].sizes[0].stock == 5
    assert unit_of_work.commits == 0


async def test_remove_size(sneaker_repository, unit_of_work) -> None:
    sneaker = await store_sneaker(sneaker_repository, "Samba")
    colorway = sneaker.add_colorway("White", "#ffffff", "AD-001")
    await sneaker_repository.save(sneaker)
    await SetSizeStock(sneaker_repository, unit_of_work).execute(
        SetSizeStockCommand(sneaker.id, colorway.id, Decimal("42.5"), 1)
    )
    remove = RemoveSize(sneaker_repository, unit_of_work)

    result = await remove.execute(RemoveSizeCommand(sneaker.id, colorway.id, Decimal("42.5")))

    assert result.colorways[0].sizes == []
    with pytest.raises(SizeVariantNotFound):
        await remove.execute(RemoveSizeCommand(sneaker.id, colorway.id, Decimal("42.5")))
