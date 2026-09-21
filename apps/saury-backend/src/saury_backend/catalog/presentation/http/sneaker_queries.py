from decimal import Decimal
from typing import Annotated

from fastapi import Query

from saury_backend.catalog.application.dtos.sneaker import ListSneakersQuery
from saury_backend.catalog.domain.repositories.sneaker_repository import SneakerSort
from saury_backend.catalog.domain.value_objects.currency import Currency
from saury_backend.catalog.domain.value_objects.gender import Gender


def list_sneakers_query(
    brand: Annotated[list[str], Query()] = [],
    category: Annotated[list[str], Query()] = [],
    gender: Annotated[list[Gender], Query()] = [],
    shoe_size: Annotated[list[Decimal], Query()] = [],
    color: Annotated[list[str], Query()] = [],
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    currency: Currency | None = None,
    in_stock: bool = False,
    q: str | None = None,
    sort: SneakerSort = SneakerSort.CREATED_AT,
    descending: bool = False,
) -> ListSneakersQuery:
    return ListSneakersQuery(
        brands=tuple(brand),
        categories=tuple(category),
        genders=tuple(value.value for value in gender),
        sizes=tuple(shoe_size),
        colors=tuple(color),
        min_price=min_price,
        max_price=max_price,
        currency=currency.value if currency else None,
        in_stock=in_stock,
        q=q,
        sort=sort.value,
        descending=descending,
    )
