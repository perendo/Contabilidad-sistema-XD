"""Cuadro de cuentas base compartido: entidad_id opcional

Revision ID: 9f3a1c7d5e20
Revises: b7c41e9a2f30
Create Date: 2026-10-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f3a1c7d5e20'
down_revision: Union[str, None] = 'b7c41e9a2f30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Una cuenta sin entidad (NULL) pertenece al cuadro base compartido.
    with op.batch_alter_table('cuentas', schema=None) as batch_op:
        batch_op.alter_column(
            'entidad_id',
            existing_type=sa.UUID(),
            nullable=True,
        )


def downgrade() -> None:
    # Las cuentas compartidas son datos sembrados y no tienen entidad a la que
    # reasignarse; se eliminan para poder restaurar el NOT NULL.
    op.execute(sa.text('DELETE FROM cuentas WHERE entidad_id IS NULL'))

    with op.batch_alter_table('cuentas', schema=None) as batch_op:
        batch_op.alter_column(
            'entidad_id',
            existing_type=sa.UUID(),
            nullable=False,
        )
