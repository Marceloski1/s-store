from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.application.unit_of_work import UnitOfWork
from shared.domain.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, PageParams
from shared.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_unit_of_work(session: SessionDep) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_page_params(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
) -> PageParams:
    return PageParams(page=page, size=size)


UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_unit_of_work)]
PageParamsDep = Annotated[PageParams, Depends(get_page_params)]
