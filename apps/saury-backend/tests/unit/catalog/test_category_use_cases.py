from uuid import uuid7

import pytest
from shared.domain.pagination import PageParams

from saury_backend.catalog.application.dtos.category import CreateCategoryCommand, UpdateCategoryCommand
from saury_backend.catalog.application.use_cases.category import (
    CreateCategory,
    DeleteCategory,
    GetCategory,
    ListCategories,
    UpdateCategory,
)
from saury_backend.catalog.domain.errors import CategoryNotFound, CategorySlugAlreadyExists


async def test_create_category_generates_slug_from_name(category_repository, unit_of_work) -> None:
    category = await CreateCategory(category_repository, unit_of_work).execute(
        CreateCategoryCommand(name="Trail Running")
    )

    assert category.slug == "trail-running"
    assert unit_of_work.commits == 1


async def test_create_category_rejects_duplicated_slug(category_repository, unit_of_work) -> None:
    create_category = CreateCategory(category_repository, unit_of_work)
    await create_category.execute(CreateCategoryCommand(name="Basketball"))

    with pytest.raises(CategorySlugAlreadyExists):
        await create_category.execute(CreateCategoryCommand(name="Lifestyle", slug="basketball"))


async def test_list_categories_returns_requested_page(category_repository, unit_of_work) -> None:
    create_category = CreateCategory(category_repository, unit_of_work)
    for name in ("Running", "Basketball", "Lifestyle"):
        await create_category.execute(CreateCategoryCommand(name=name))

    page = await ListCategories(category_repository).execute(PageParams(page=2, size=2))

    assert [category.name for category in page.items] == ["Running"]
    assert page.total == 3


async def test_update_category_rejects_slug_of_another_category(category_repository, unit_of_work) -> None:
    create_category = CreateCategory(category_repository, unit_of_work)
    await create_category.execute(CreateCategoryCommand(name="Running"))
    lifestyle = await create_category.execute(CreateCategoryCommand(name="Lifestyle"))

    with pytest.raises(CategorySlugAlreadyExists):
        await UpdateCategory(category_repository, unit_of_work).execute(
            UpdateCategoryCommand(category_id=lifestyle.id, name="Lifestyle", slug="running")
        )


async def test_delete_category_removes_it(category_repository, unit_of_work) -> None:
    created = await CreateCategory(category_repository, unit_of_work).execute(CreateCategoryCommand(name="Running"))

    await DeleteCategory(category_repository, unit_of_work).execute(created.id)

    with pytest.raises(CategoryNotFound):
        await GetCategory(category_repository).execute(created.id)


async def test_get_category_raises_when_missing(category_repository) -> None:
    with pytest.raises(CategoryNotFound):
        await GetCategory(category_repository).execute(uuid7())
