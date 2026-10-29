"""Idempotencia e índice de los documentos adjuntos

Revision ID: 5d7e9b2c4a10
Revises: 4c2f8a1b6d90
Create Date: 2026-10-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d7e9b2c4a10'
down_revision: Union[str, None] = '4c2f8a1b6d90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('documentos_adjuntos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('clave_idempotencia', sa.String(), nullable=True))
        batch_op.create_unique_constraint(
            'uq_documentos_asiento_clave', ['asiento_id', 'clave_idempotencia']
        )
        batch_op.create_index('ix_documentos_adjuntos_asiento_id', ['asiento_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('documentos_adjuntos', schema=None) as batch_op:
        batch_op.drop_index('ix_documentos_adjuntos_asiento_id')
        batch_op.drop_constraint('uq_documentos_asiento_clave', type_='unique')
        batch_op.drop_column('clave_idempotencia')
