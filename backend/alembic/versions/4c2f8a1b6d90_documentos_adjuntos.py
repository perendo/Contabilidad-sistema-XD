"""Documentos adjuntos a los asientos

Revision ID: 4c2f8a1b6d90
Revises: 9f3a1c7d5e20
Create Date: 2026-10-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c2f8a1b6d90'
down_revision: Union[str, None] = '9f3a1c7d5e20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('documentos_adjuntos',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('asiento_id', sa.UUID(), nullable=False),
    sa.Column('nombre', sa.String(), nullable=False),
    sa.Column('tipo_contenido', sa.String(), nullable=False),
    sa.Column('tamano', sa.Integer(), nullable=False),
    sa.Column('ruta', sa.String(), nullable=False),
    sa.Column('subido_por_id', sa.UUID(), nullable=False),
    sa.Column('creado_en', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['asiento_id'], ['asientos.id'], ),
    sa.ForeignKeyConstraint(['subido_por_id'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('documentos_adjuntos')
