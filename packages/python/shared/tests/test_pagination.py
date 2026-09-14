import pytest

from shared.domain.errors import ValidationError
from shared.domain.pagination import MAX_PAGE_SIZE, Page, PageParams


def test_page_params_calculates_offset() -> None:
    assert PageParams(page=3, size=10).offset == 20


@pytest.mark.parametrize(("page", "size"), [(0, 10), (1, 0), (1, MAX_PAGE_SIZE + 1)])
def test_page_params_rejects_out_of_range_values(page: int, size: int) -> None:
    with pytest.raises(ValidationError):
        PageParams(page=page, size=size)


@pytest.mark.parametrize(("total", "expected_pages"), [(0, 0), (1, 1), (20, 2), (21, 3)])
def test_page_calculates_total_pages(total: int, expected_pages: int) -> None:
    assert Page(items=[], total=total, page=1, size=10).pages == expected_pages


def test_page_map_transforms_items_and_keeps_metadata() -> None:
    page = Page(items=[1, 2], total=5, page=2, size=2)

    mapped = page.map(str)

    assert mapped == Page(items=["1", "2"], total=5, page=2, size=2)
