"""create users

Revision ID: 8e9ea7103b04
Revises: 60a0e61ba848
Create Date: 2026-09-21 17:12:04.356823

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '8e9ea7103b04'
down_revision: str | Sequence[str] | None = '60a0e61ba848'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'SUPER_ADMIN', name='role', native_enum=False, create_constraint=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )


def downgrade() -> None:
    op.drop_table('users')
