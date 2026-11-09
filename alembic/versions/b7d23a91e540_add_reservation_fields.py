"""add_reservation_fields_to_equipment

Revision ID: b7d23a91e540
Revises: 548dbf62fd0a
Create Date: 2026-11-02 12:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7d23a91e540'
down_revision: Union[str, Sequence[str], None] = '548dbf62fd0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('equipment_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reservation_code', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('reservation_customer', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('reservation_note', sa.String(length=200), nullable=True))
        batch_op.create_index(batch_op.f('ix_equipment_items_reservation_code'), ['reservation_code'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('equipment_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_equipment_items_reservation_code'))
        batch_op.drop_column('reservation_note')
        batch_op.drop_column('reservation_customer')
        batch_op.drop_column('reservation_code')
