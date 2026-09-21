from uuid import uuid7

import pytest
from shared.domain.errors import ValidationError
from shared.domain.money import Money
from shared.domain.slug import Slug

from saury_backend.catalog.domain.entities.sneaker import MAX_IMAGES_PER_SNEAKER, Sneaker
from saury_backend.catalog.domain.errors import (
    ColorwayNotFound,
    CurrencyMismatch,
    ImageLimitExceeded,
    ImageNotFound,
    InvalidSneakerStatusTransition,
    SizeVariantNotFound,
    SkuAlreadyExists,
    SneakerNotPublishable,
)
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize
from saury_backend.catalog.domain.value_objects.sneaker_status import SneakerStatus
from saury_backend.catalog.domain.value_objects.spec_sheet import SpecSheet
from saury_backend.catalog.domain.value_objects.testimonial import Testimonial as CustomerTestimonial


def make_sneaker(base_price: Money | None = None) -> Sneaker:
    return Sneaker.create(
        name="Air Max 90",
        description="Classic runner",
        brand_id=uuid7(),
        category_id=uuid7(),
        gender=Gender.UNISEX,
        base_price=base_price or Money.of("130", "USD"),
    )


def make_publishable_sneaker() -> Sneaker:
    sneaker = make_sneaker()
    colorway = sneaker.add_colorway("Infrared", "#ff0000", "am90-inf")
    sneaker.set_size_stock(colorway.id, ShoeSize.of("42"), 3)
    sneaker.add_image("sauri-store/air-max", "https://images.test/air-max")
    return sneaker


class TestCreation:
    def test_creates_draft_with_generated_slug(self) -> None:
        sneaker = make_sneaker()

        assert sneaker.status is SneakerStatus.DRAFT
        assert sneaker.slug == Slug("air-max-90")
        assert sneaker.created_at == sneaker.updated_at
        assert sneaker.colorways == []
        assert sneaker.images == []

    @pytest.mark.parametrize("name", ["", "   ", "a" * 151])
    def test_rejects_invalid_names(self, name: str) -> None:
        with pytest.raises(ValidationError):
            Sneaker.create(name, "", uuid7(), uuid7(), Gender.MEN, Money.of("10", "USD"))

    def test_rejects_too_long_description(self) -> None:
        with pytest.raises(ValidationError):
            Sneaker.create("Air Max", "a" * 2001, uuid7(), uuid7(), Gender.MEN, Money.of("10", "USD"))

    def test_update_refreshes_fields_and_timestamp(self) -> None:
        sneaker = make_sneaker()
        previous_update = sneaker.updated_at

        sneaker.update(
            name="Air Max 95",
            description="",
            brand_id=sneaker.brand_id,
            category_id=sneaker.category_id,
            gender=Gender.MEN,
            base_price=Money.of("150", "EUR"),
            slug=Slug("am95"),
        )

        assert (sneaker.name, sneaker.slug, sneaker.gender) == ("Air Max 95", Slug("am95"), Gender.MEN)
        assert sneaker.base_price == Money.of("150", "EUR")
        assert sneaker.updated_at >= previous_update


class TestColorways:
    def test_effective_price_uses_override_or_base_price(self) -> None:
        sneaker = make_sneaker()
        regular = sneaker.add_colorway("Black", "#000000", "AM90-BLK")
        special = sneaker.add_colorway("Gold", "#ffd700", "AM90-GLD", Money.of("180", "USD"))

        assert regular.effective_price(sneaker.base_price) == Money.of("130", "USD")
        assert special.effective_price(sneaker.base_price) == Money.of("180", "USD")

    def test_normalizes_sku_and_color_code(self) -> None:
        colorway = make_sneaker().add_colorway("Black", "#abcdef", " am90-blk ")

        assert (colorway.sku, colorway.color_code) == ("AM90-BLK", "#ABCDEF")

    @pytest.mark.parametrize(("color_code", "sku"), [("red", "AM90"), ("#FFF", "AM90"), ("#000000", "AM 90"), ("#000000", "")])
    def test_rejects_invalid_color_code_or_sku(self, color_code: str, sku: str) -> None:
        with pytest.raises(ValidationError):
            make_sneaker().add_colorway("Black", color_code, sku)

    def test_rejects_duplicate_sku_within_sneaker(self) -> None:
        sneaker = make_sneaker()
        sneaker.add_colorway("Black", "#000000", "AM90-BLK")

        with pytest.raises(SkuAlreadyExists):
            sneaker.add_colorway("Black 2", "#111111", "am90-blk")

    def test_update_colorway_keeps_its_own_sku(self) -> None:
        sneaker = make_sneaker()
        colorway = sneaker.add_colorway("Black", "#000000", "AM90-BLK")

        updated = sneaker.update_colorway(colorway.id, "Triple Black", "#000000", "AM90-BLK", None)

        assert updated.name == "Triple Black"

    def test_rejects_override_in_other_currency(self) -> None:
        with pytest.raises(CurrencyMismatch):
            make_sneaker().add_colorway("Black", "#000000", "AM90-BLK", Money.of("100", "EUR"))

    def test_rejects_base_price_currency_change_with_overrides(self) -> None:
        sneaker = make_sneaker()
        sneaker.add_colorway("Gold", "#ffd700", "AM90-GLD", Money.of("180", "USD"))

        with pytest.raises(CurrencyMismatch):
            sneaker.update(
                sneaker.name, "", sneaker.brand_id, sneaker.category_id, sneaker.gender, Money.of("150", "EUR")
            )
        assert sneaker.base_price.currency == "USD"

    def test_remove_unknown_colorway_fails(self) -> None:
        with pytest.raises(ColorwayNotFound):
            make_sneaker().remove_colorway(uuid7())


class TestSizes:
    def test_set_size_stock_adds_then_adjusts_variant(self) -> None:
        sneaker = make_sneaker()
        colorway = sneaker.add_colorway("Black", "#000000", "AM90-BLK")

        sneaker.set_size_stock(colorway.id, ShoeSize.of("43"), 2)
        sneaker.set_size_stock(colorway.id, ShoeSize.of("42.5"), 1)
        sneaker.set_size_stock(colorway.id, ShoeSize.of("43"), 7)

        assert [(str(v.size), v.stock) for v in colorway.sizes] == [("42.5", 1), ("43", 7)]

    def test_rejects_negative_stock_without_changes(self) -> None:
        sneaker = make_sneaker()
        colorway = sneaker.add_colorway("Black", "#000000", "AM90-BLK")
        sneaker.set_size_stock(colorway.id, ShoeSize.of("42"), 5)

        with pytest.raises(ValidationError):
            sneaker.set_size_stock(colorway.id, ShoeSize.of("42"), -1)
        assert colorway.sizes[0].stock == 5

    def test_remove_size(self) -> None:
        sneaker = make_sneaker()
        colorway = sneaker.add_colorway("Black", "#000000", "AM90-BLK")
        sneaker.set_size_stock(colorway.id, ShoeSize.of("42"), 5)

        sneaker.remove_size(colorway.id, ShoeSize.of("42"))

        assert colorway.sizes == []
        with pytest.raises(SizeVariantNotFound):
            sneaker.remove_size(colorway.id, ShoeSize.of("42"))

    @pytest.mark.parametrize("value", ["0", "-1", "42.3", "100", "NaN", "abc"])
    def test_rejects_invalid_eu_sizes(self, value: str) -> None:
        with pytest.raises(ValidationError):
            ShoeSize.of(value)


class TestImages:
    def test_first_image_is_primary_and_positions_are_consecutive(self) -> None:
        sneaker = make_sneaker()

        first = sneaker.add_image("p/1", "https://images.test/1")
        second = sneaker.add_image("p/2", "https://images.test/2", alt="Side")

        assert (first.position, first.is_primary) == (0, True)
        assert (second.position, second.is_primary, second.alt) == (1, False, "Side")

    def test_mark_primary_unmarks_previous(self) -> None:
        sneaker = make_sneaker()
        first = sneaker.add_image("p/1", "https://images.test/1")
        second = sneaker.add_image("p/2", "https://images.test/2")

        sneaker.mark_primary_image(second.id)

        assert [image.is_primary for image in sneaker.images] == [False, True]
        assert sneaker.primary_image is second
        assert first.is_primary is False

    def test_remove_image_renumbers_and_promotes_new_primary(self) -> None:
        sneaker = make_sneaker()
        first = sneaker.add_image("p/1", "https://images.test/1")
        sneaker.add_image("p/2", "https://images.test/2")
        third = sneaker.add_image("p/3", "https://images.test/3")

        removed = sneaker.remove_image(first.id)

        assert removed is first
        assert [image.position for image in sneaker.images] == [0, 1]
        assert sneaker.images[0].is_primary
        assert sum(image.is_primary for image in sneaker.images) == 1
        assert third.position == 1

    def test_reorder_images(self) -> None:
        sneaker = make_sneaker()
        ids = [sneaker.add_image(f"p/{i}", f"https://images.test/{i}").id for i in range(3)]

        sneaker.reorder_images(list(reversed(ids)))

        assert [(image.id, image.position) for image in sneaker.images] == [(ids[2], 0), (ids[1], 1), (ids[0], 2)]

    @pytest.mark.parametrize("order", ["missing", "duplicated", "unknown"])
    def test_reorder_requires_every_image_once(self, order: str) -> None:
        sneaker = make_sneaker()
        ids = [sneaker.add_image(f"p/{i}", f"https://images.test/{i}").id for i in range(2)]
        invalid = {"missing": ids[:1], "duplicated": [ids[0], ids[0]], "unknown": [ids[0], uuid7()]}[order]

        with pytest.raises(ValidationError):
            sneaker.reorder_images(invalid)

    def test_limits_images_per_sneaker(self) -> None:
        sneaker = make_sneaker()
        for i in range(MAX_IMAGES_PER_SNEAKER):
            sneaker.add_image(f"p/{i}", f"https://images.test/{i}")

        with pytest.raises(ImageLimitExceeded):
            sneaker.add_image("p/extra", "https://images.test/extra")

    def test_unknown_image_fails(self) -> None:
        with pytest.raises(ImageNotFound):
            make_sneaker().mark_primary_image(uuid7())


class TestStatusTransitions:
    def test_publish_archive_and_unarchive_cycle(self) -> None:
        sneaker = make_publishable_sneaker()

        sneaker.publish()
        assert sneaker.status is SneakerStatus.ACTIVE
        sneaker.archive()
        assert sneaker.status is SneakerStatus.ARCHIVED
        sneaker.unarchive()
        assert sneaker.status is SneakerStatus.DRAFT

    def test_publish_requires_primary_image(self) -> None:
        sneaker = make_sneaker()
        colorway = sneaker.add_colorway("Black", "#000000", "AM90-BLK")
        sneaker.set_size_stock(colorway.id, ShoeSize.of("42"), 1)

        with pytest.raises(SneakerNotPublishable, match="primary image"):
            sneaker.publish()
        assert sneaker.status is SneakerStatus.DRAFT

    def test_publish_requires_colorway_with_size(self) -> None:
        sneaker = make_sneaker()
        sneaker.add_image("p/1", "https://images.test/1")
        sneaker.add_colorway("Black", "#000000", "AM90-BLK")

        with pytest.raises(SneakerNotPublishable, match="colorway with a size"):
            sneaker.publish()

    @pytest.mark.parametrize(
        ("setup", "transition"),
        [
            ([], "archive"),
            ([], "unarchive"),
            (["publish"], "publish"),
            (["publish"], "unarchive"),
            (["publish", "archive"], "publish"),
            (["publish", "archive"], "archive"),
        ],
    )
    def test_rejects_invalid_transitions(self, setup: list[str], transition: str) -> None:
        sneaker = make_publishable_sneaker()
        for step in setup:
            getattr(sneaker, step)()

        with pytest.raises(InvalidSneakerStatusTransition):
            getattr(sneaker, transition)()


class TestContent:
    def test_defaults_to_empty_content(self) -> None:
        sneaker = make_sneaker()

        assert (sneaker.reference, sneaker.specs, sneaker.usage, sneaker.testimonial) == (None, SpecSheet(), "", None)

    def test_normalizes_content_on_update(self) -> None:
        sneaker = make_sneaker()

        sneaker.update(
            name="Air Max 90",
            description="",
            brand_id=sneaker.brand_id,
            category_id=sneaker.category_id,
            gender=Gender.UNISEX,
            base_price=sneaker.base_price,
            reference=" als-am90-001 ",
            specs=SpecSheet(material=" Mesh ", weight="310 g"),
            usage=" Running diario ",
            testimonial=CustomerTestimonial(quote=" Muy cómodas ", author="Ana, talla 38"),
        )

        assert sneaker.reference == "ALS-AM90-001"
        assert sneaker.specs == SpecSheet(material="Mesh", weight="310 g")
        assert sneaker.usage == "Running diario"
        assert sneaker.testimonial == CustomerTestimonial(quote="Muy cómodas", author="Ana, talla 38")

    def test_blank_reference_is_cleared(self) -> None:
        sneaker = Sneaker.create("Air Max", "", uuid7(), uuid7(), Gender.MEN, Money.of("10", "USD"), reference="  ")

        assert sneaker.reference is None

    @pytest.mark.parametrize("reference", ["ALS 001", "als_001", "A" * 65])
    def test_rejects_invalid_references(self, reference: str) -> None:
        with pytest.raises(ValidationError):
            Sneaker.create("Air Max", "", uuid7(), uuid7(), Gender.MEN, Money.of("10", "USD"), reference=reference)

    def test_rejects_too_long_usage(self) -> None:
        with pytest.raises(ValidationError):
            Sneaker.create("Air Max", "", uuid7(), uuid7(), Gender.MEN, Money.of("10", "USD"), usage="a" * 501)

    def test_rejects_too_long_spec_values(self) -> None:
        with pytest.raises(ValidationError):
            SpecSheet(material="a" * 101)

    @pytest.mark.parametrize(("quote", "author"), [("", "Ana"), ("Muy cómodas", "  "), ("a" * 501, "Ana")])
    def test_rejects_invalid_testimonials(self, quote: str, author: str) -> None:
        with pytest.raises(ValidationError):
            CustomerTestimonial(quote=quote, author=author)
