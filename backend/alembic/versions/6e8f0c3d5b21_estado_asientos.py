"""Estado de los asientos (borrador o registrado)

Revision ID: 6e8f0c3d5b21
Revises: 5d7e9b2c4a10
Create Date: 2026-10-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6e8f0c3d5b21"
down_revision: Union[str, None] = "5d7e9b2c4a10"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("asientos", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "estado",
                sa.Enum("borrador", "registrado", name="estadoasiento"),
                nullable=False,
                server_default="registrado",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("asientos", schema=None) as batch_op:
        batch_op.drop_column("estado")