"""create sneakers catalog

Revision ID: 62841e421959
Revises: e66d92fefe47
Create Date: 2026-09-17 13:22:14.452855

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '62841e421959'
down_revision: str | Sequence[str] | None = 'e66d92fefe47'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('sneakers',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('slug', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=2000), nullable=False),
    sa.Column('brand_id', sa.Uuid(), nullable=False),
    sa.Column('category_id', sa.Uuid(), nullable=False),
    sa.Column('gender', sa.Enum('men', 'women', 'unisex', 'kids', name='gender', native_enum=False, create_constraint=True), nullable=False),
    sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('status', sa.Enum('draft', 'active', 'archived', name='status', native_enum=False, create_constraint=True), nullable=False),
    sa.Column('release_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('base_price >= 0', name=op.f('ck_sneakers_base_price_non_negative')),
    sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], name=op.f('fk_sneakers_brand_id_brands'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_sneakers_category_id_categories'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sneakers')),
    sa.UniqueConstraint('slug', name=op.f('uq_sneakers_slug'))
    )
    op.create_index(op.f('ix_sneakers_brand_id'), 'sneakers', ['brand_id'], unique=False)
    op.create_index(op.f('ix_sneakers_category_id'), 'sneakers', ['category_id'], unique=False)
    op.create_index('ix_sneakers_currency_base_price', 'sneakers', ['currency', 'base_price'], unique=False)
    op.create_index(op.f('ix_sneakers_status'), 'sneakers', ['status'], unique=False)
    op.create_table('colorways',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('sneaker_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('color_code', sa.String(length=7), nullable=False),
    sa.Column('sku', sa.String(length=64), nullable=False),
    sa.Column('price_override', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.CheckConstraint('price_override >= 0', name=op.f('ck_colorways_price_override_non_negative')),
    sa.ForeignKeyConstraint(['sneaker_id'], ['sneakers.id'], name=op.f('fk_colorways_sneaker_id_sneakers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_colorways')),
    sa.UniqueConstraint('sku', name=op.f('uq_colorways_sku'))
    )
    op.create_index(op.f('ix_colorways_sneaker_id'), 'colorways', ['sneaker_id'], unique=False)
    op.create_table('sneaker_images',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('sneaker_id', sa.Uuid(), nullable=False),
    sa.Column('public_id', sa.String(length=255), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('alt', sa.String(length=200), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.CheckConstraint('position >= 0', name=op.f('ck_sneaker_images_position_non_negative')),
    sa.ForeignKeyConstraint(['sneaker_id'], ['sneakers.id'], name=op.f('fk_sneaker_images_sneaker_id_sneakers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sneaker_images'))
    )
    op.create_index(op.f('ix_sneaker_images_sneaker_id'), 'sneaker_images', ['sneaker_id'], unique=False)
    op.create_table('size_variants',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('colorway_id', sa.Uuid(), nullable=False),
    sa.Column('size', sa.Numeric(precision=3, scale=1), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.CheckConstraint('size > 0', name=op.f('ck_size_variants_size_positive')),
    sa.CheckConstraint('stock >= 0', name=op.f('ck_size_variants_stock_non_negative')),
    sa.ForeignKeyConstraint(['colorway_id'], ['colorways.id'], name=op.f('fk_size_variants_colorway_id_colorways'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_size_variants')),
    sa.UniqueConstraint('colorway_id', 'size', name='uq_size_variants_colorway_id_size')
    )
    op.create_index(op.f('ix_size_variants_colorway_id'), 'size_variants', ['colorway_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_size_variants_colorway_id'), table_name='size_variants')
    op.drop_table('size_variants')
    op.drop_index(op.f('ix_sneaker_images_sneaker_id'), table_name='sneaker_images')
    op.drop_table('sneaker_images')
    op.drop_index(op.f('ix_colorways_sneaker_id'), table_name='colorways')
    op.drop_table('colorways')
    op.drop_index(op.f('ix_sneakers_status'), table_name='sneakers')
    op.drop_index('ix_sneakers_currency_base_price', table_name='sneakers')
    op.drop_index(op.f('ix_sneakers_category_id'), table_name='sneakers')
    op.drop_index(op.f('ix_sneakers_brand_id'), table_name='sneakers')
    op.drop_table('sneakers')
