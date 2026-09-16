from uuid import uuid7

import pytest
from shared.domain.money import Money

from saury_backend.catalog.application.dtos.sneaker import ReorderSneakerImagesCommand, UploadSneakerImageCommand
from saury_backend.catalog.application.use_cases.image import (
    DeleteSneakerImage,
    MarkPrimarySneakerImage,
    ReorderSneakerImages,
    UploadSneakerImage,
)
from saury_backend.catalog.application.use_cases.publication import ArchiveSneaker, PublishSneaker, UnarchiveSneaker
from saury_backend.catalog.application.use_cases.sneaker import GetSneaker
from saury_backend.catalog.domain.entities.sneaker import MAX_IMAGES_PER_SNEAKER, Sneaker
from saury_backend.catalog.domain.errors import (
    ImageLimitExceeded,
    ImageNotFound,
    InvalidSneakerStatusTransition,
    SneakerNotFound,
    SneakerNotPublishable,
)
from saury_backend.catalog.domain.value_objects.gender import Gender
from saury_backend.catalog.domain.value_objects.shoe_size import ShoeSize

FOLDER = "sauri-store/test"


@pytest.fixture
async def sneaker(sneaker_repository) -> Sneaker:
    sneaker = Sneaker.create("Air Max 90", "", uuid7(), uuid7(), Gender.UNISEX, Money.of("130", "USD"))
    await sneaker_repository.save(sneaker)
    return sneaker


@pytest.fixture
def upload(sneaker_repository, image_storage, unit_of_work) -> UploadSneakerImage:
    return UploadSneakerImage(sneaker_repository, image_storage, unit_of_work, FOLDER)


async def upload_images(upload: UploadSneakerImage, sneaker: Sneaker, count: int) -> list:
    result = None
    for index in range(count):
        result = await upload.execute(UploadSneakerImageCommand(sneaker.id, b"png", f"{index}.png", alt=f"View {index}"))
    return result.images if result else []


async def test_upload_stores_image_under_sneaker_folder(upload, sneaker, image_storage, unit_of_work) -> None:
    result = await upload.execute(UploadSneakerImageCommand(sneaker.id, b"png-bytes", "front.png", alt="Front"))

    [image] = result.images
    [stored] = image_storage.uploaded
    assert stored.public_id.startswith(f"{FOLDER}/sneakers/{sneaker.id}/")
    assert (image.public_id, image.url, image.alt) == (stored.public_id, stored.url, "Front")
    assert (image.position, image.is_primary) == (0, True)
    assert unit_of_work.commits == 1


async def test_upload_requires_existing_sneaker_before_uploading(upload, image_storage) -> None:
    with pytest.raises(SneakerNotFound):
        await upload.execute(UploadSneakerImageCommand(uuid7(), b"png", "front.png"))
    assert image_storage.uploaded == []


async def test_upload_rejects_images_over_limit_before_uploading(upload, sneaker, image_storage) -> None:
    await upload_images(upload, sneaker, MAX_IMAGES_PER_SNEAKER)

    with pytest.raises(ImageLimitExceeded):
        await upload.execute(UploadSneakerImageCommand(sneaker.id, b"png", "extra.png"))
    assert len(image_storage.uploaded) == MAX_IMAGES_PER_SNEAKER


async def test_upload_deletes_stored_image_when_commit_fails(
    upload, sneaker, sneaker_repository, image_storage, unit_of_work
) -> None:
    unit_of_work.fail_on_commit = True

    with pytest.raises(Exception, match="commit failed"):
        await upload.execute(UploadSneakerImageCommand(sneaker.id, b"png", "front.png"))

    [stored] = image_storage.uploaded
    assert image_storage.deleted == [stored.public_id]
    assert image_storage.images == {}
    assert unit_of_work.rollbacks == 1


async def test_upload_keeps_original_error_when_compensation_fails(
    upload, sneaker, image_storage, unit_of_work, caplog
) -> None:
    unit_of_work.fail_on_commit = True
    image_storage.fail_on_delete = True

    with pytest.raises(Exception, match="commit failed"):
        await upload.execute(UploadSneakerImageCommand(sneaker.id, b"png", "front.png"))

    assert "Failed to delete stored image" in caplog.text


async def test_delete_image_removes_it_from_storage(upload, sneaker, sneaker_repository, image_storage, unit_of_work) -> None:
    first, second = await upload_images(upload, sneaker, 2)

    result = await DeleteSneakerImage(sneaker_repository, image_storage, unit_of_work).execute(sneaker.id, first.id)

    assert [(image.id, image.position, image.is_primary) for image in result.images] == [(second.id, 0, True)]
    assert image_storage.deleted == [first.public_id]


async def test_delete_image_tolerates_storage_failures(
    upload, sneaker, sneaker_repository, image_storage, unit_of_work, caplog
) -> None:
    [image] = await upload_images(upload, sneaker, 1)
    image_storage.fail_on_delete = True

    result = await DeleteSneakerImage(sneaker_repository, image_storage, unit_of_work).execute(sneaker.id, image.id)

    assert result.images == []
    assert (await GetSneaker(sneaker_repository).execute(sneaker.id)).images == []
    assert image.public_id in caplog.text


async def test_delete_unknown_image_does_not_touch_storage(sneaker, sneaker_repository, image_storage, unit_of_work) -> None:
    with pytest.raises(ImageNotFound):
        await DeleteSneakerImage(sneaker_repository, image_storage, unit_of_work).execute(sneaker.id, uuid7())
    assert image_storage.deleted == []


async def test_reorder_and_mark_primary(upload, sneaker, sneaker_repository, unit_of_work) -> None:
    first, second, third = await upload_images(upload, sneaker, 3)

    reordered = await ReorderSneakerImages(sneaker_repository, unit_of_work).execute(
        ReorderSneakerImagesCommand(sneaker.id, [third.id, first.id, second.id])
    )
    marked = await MarkPrimarySneakerImage(sneaker_repository, unit_of_work).execute(sneaker.id, third.id)

    assert [image.id for image in reordered.images] == [third.id, first.id, second.id]
    assert [image.is_primary for image in marked.images] == [True, False, False]


async def test_publication_lifecycle(upload, sneaker, sneaker_repository, unit_of_work) -> None:
    colorway = sneaker.add_colorway("Infrared", "#ff0000", "AM90-INF")
    sneaker.set_size_stock(colorway.id, ShoeSize.of("42"), 2)
    await sneaker_repository.save(sneaker)
    await upload_images(upload, sneaker, 1)

    assert (await PublishSneaker(sneaker_repository, unit_of_work).execute(sneaker.id)).status == "active"
    assert (await ArchiveSneaker(sneaker_repository, unit_of_work).execute(sneaker.id)).status == "archived"
    assert (await UnarchiveSneaker(sneaker_repository, unit_of_work).execute(sneaker.id)).status == "draft"


async def test_publish_without_primary_image_is_rejected(sneaker, sneaker_repository, unit_of_work) -> None:
    with pytest.raises(SneakerNotPublishable, match="primary image"):
        await PublishSneaker(sneaker_repository, unit_of_work).execute(sneaker.id)

    assert (await GetSneaker(sneaker_repository).execute(sneaker.id)).status == "draft"
    assert unit_of_work.commits == 0


async def test_invalid_transition_is_rejected(sneaker, sneaker_repository, unit_of_work) -> None:
    with pytest.raises(InvalidSneakerStatusTransition):
        await ArchiveSneaker(sneaker_repository, unit_of_work).execute(sneaker.id)
