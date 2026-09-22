from uuid import uuid7

import pytest
from shared.domain.errors import CommonErrorCode, ValidationError
from shared.domain.money import Money

from saury_backend.catalog.domain.entities.colorway import normalize_sku
from saury_backend.catalog.domain.entities.sneaker import Sneaker
from saury_backend.catalog.domain.error_codes import CatalogErrorCode
from saury_backend.catalog.domain.errors import (
    BrandNotFound,
    CurrencyMismatch,
    ImageLimitExceeded,
    InvalidSneakerStatusTransition,
    SkuAlreadyExists,
    SneakerNeedsPrimaryImage,
    SneakerNeedsSizedColorway,
)
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.domain.value_objects.spec_sheet import SpecSheet


def make_sneaker() -> Sneaker:
    return Sneaker.create("Air Max", "", uuid7(), uuid7(), Gender.UNISEX, Money.of("100", "USD"))


def test_domain_errors_expose_codes_and_params() -> None:
    brand_id = uuid7()

    assert (BrandNotFound(brand_id).code, BrandNotFound(brand_id).params) == (
        CatalogErrorCode.BRAND_NOT_FOUND,
        {"id": str(brand_id)},
    )
    assert SkuAlreadyExists("AM-1").params == {"sku": "AM-1"}
    assert ImageLimitExceeded(8).params == {"limit": 8}
    assert CurrencyMismatch(expected="USD", actual="EUR").params == {"expected": "USD", "actual": "EUR"}
    transition = InvalidSneakerStatusTransition(SneakerStatus.DRAFT, SneakerStatus.ARCHIVED)
    assert (transition.code, transition.params) == (
        CatalogErrorCode.INVALID_STATUS_TRANSITION,
        {"from": "DRAFT", "to": "ARCHIVED"},
    )


def test_publish_explains_each_missing_requirement_with_its_own_code() -> None:
    sneaker = make_sneaker()

    with pytest.raises(SneakerNeedsPrimaryImage) as missing_image:
        sneaker.publish()
    sneaker.add_image("p/front", "https://images.test/front")
    with pytest.raises(SneakerNeedsSizedColorway) as missing_sizes:
        sneaker.publish()

    assert missing_image.value.code == CatalogErrorCode.SNEAKER_NEEDS_PRIMARY_IMAGE
    assert missing_sizes.value.code == CatalogErrorCode.SNEAKER_NEEDS_SIZED_COLORWAY


@pytest.mark.parametrize(
    ("action", "code", "params"),
    [
        (lambda: ShoeSize.of("42.3"), CatalogErrorCode.INVALID_SHOE_SIZE, {"value": "42.3", "max": "99.5"}),
        (lambda: normalize_sku("bad sku"), CatalogErrorCode.INVALID_SKU, {"value": "bad sku", "max": 64}),
        (
            lambda: SpecSheet(material="a" * 101),
            CommonErrorCode.TEXT_TOO_LONG,
            {"field": "material", "max": 100},
        ),
        (
            lambda: make_sneaker().add_colorway("Red", "red", "AM-RED"),
            CatalogErrorCode.INVALID_COLOR_CODE,
            {"value": "red"},
        ),
    ],
    ids=["shoe-size", "sku", "spec-too-long", "color-code"],
)
def test_value_validations_raise_coded_errors(action, code: str, params: dict[str, object]) -> None:
    with pytest.raises(ValidationError) as raised:
        action()

    assert (raised.value.code, raised.value.params) == (code, params)
