"""Unicidad del número de asiento por entidad y ejercicio

Revision ID: 7a0b1c2d3e4f
Revises: 6e8f0c3d5b21
Create Date: 2026-10-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a0b1c2d3e4f"
down_revision: Union[str, None] = "6e8f0c3d5b21"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("asientos", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_asientos_entidad_ejercicio_numero", ["entidad_id", "ejercicio_id", "numero_asiento"]
        )


def downgrade() -> None:
    with op.batch_alter_table("asientos", schema=None) as batch_op:
        batch_op.drop_constraint("uq_asientos_entidad_ejercicio_numero", type_="unique")