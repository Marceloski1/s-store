"""uppercase sneaker enums

Revision ID: 3c1f5a9d2b7e
Revises: 8e9ea7103b04
Create Date: 2026-09-21 18:00:00.000000

"""
from collections.abc import Sequence

from alembic import op


revision: str = '3c1f5a9d2b7e'
down_revision: str | Sequence[str] | None = '8e9ea7103b04'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_COLUMNS = {
    'gender': ('men', 'women', 'unisex', 'kids'),
    'status': ('draft', 'active', 'archived'),
}


def _values(values: Sequence[str]) -> str:
    return ', '.join(f"'{value}'" for value in values)


def _convert(transform: str, case: str) -> None:
    for column, values in _COLUMNS.items():
        converted = [getattr(value, case)() for value in values]
        op.drop_constraint(op.f(f'ck_sneakers_{column}'), 'sneakers', type_='check')
        op.execute(f'UPDATE sneakers SET {column} = {transform}({column})')
        op.create_check_constraint(op.f(f'ck_sneakers_{column}'), 'sneakers', f'{column} IN ({_values(converted)})')


def upgrade() -> None:
    _convert('upper', 'upper')


def downgrade() -> None:
    _convert('lower', 'lower')
