"""add sneaker sales content

Revision ID: 60a0e61ba848
Revises: 62841e421959
Create Date: 2026-09-21 16:27:24.422722

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = '60a0e61ba848'
down_revision: str | Sequence[str] | None = '62841e421959'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('sneakers', sa.Column('reference', sa.String(length=64), nullable=True))
    op.add_column('sneakers', sa.Column('material', sa.String(length=100), server_default='', nullable=False))
    op.add_column('sneakers', sa.Column('technology', sa.String(length=100), server_default='', nullable=False))
    op.add_column('sneakers', sa.Column('weight', sa.String(length=100), server_default='', nullable=False))
    op.add_column('sneakers', sa.Column('cushioning', sa.String(length=100), server_default='', nullable=False))
    op.add_column('sneakers', sa.Column('usage', sa.String(length=500), server_default='', nullable=False))
    op.add_column('sneakers', sa.Column('testimonial_quote', sa.String(length=500), nullable=True))
    op.add_column('sneakers', sa.Column('testimonial_author', sa.String(length=100), nullable=True))
    op.create_unique_constraint(op.f('uq_sneakers_reference'), 'sneakers', ['reference'])
    op.create_check_constraint(
        op.f('ck_sneakers_testimonial_complete'),
        'sneakers',
        '(testimonial_quote IS NULL) = (testimonial_author IS NULL)',
    )


def downgrade() -> None:
    op.drop_constraint(op.f('ck_sneakers_testimonial_complete'), 'sneakers', type_='check')
    op.drop_constraint(op.f('uq_sneakers_reference'), 'sneakers', type_='unique')
    op.drop_column('sneakers', 'testimonial_author')
    op.drop_column('sneakers', 'testimonial_quote')
    op.drop_column('sneakers', 'usage')
    op.drop_column('sneakers', 'cushioning')
    op.drop_column('sneakers', 'weight')
    op.drop_column('sneakers', 'technology')
    op.drop_column('sneakers', 'material')
    op.drop_column('sneakers', 'reference')
