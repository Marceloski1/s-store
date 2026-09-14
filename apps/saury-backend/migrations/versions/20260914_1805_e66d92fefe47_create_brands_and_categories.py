"""create brands and categories

Revision ID: e66d92fefe47
Revises:
Create Date: 2026-09-14 18:05:07.588788

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = 'e66d92fefe47'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('brands',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_brands')),
    sa.UniqueConstraint('slug', name=op.f('uq_brands_slug'))
    )
    op.create_table('categories',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
    sa.UniqueConstraint('slug', name=op.f('uq_categories_slug'))
    )


def downgrade() -> None:
    op.drop_table('categories')
    op.drop_table('brands')
