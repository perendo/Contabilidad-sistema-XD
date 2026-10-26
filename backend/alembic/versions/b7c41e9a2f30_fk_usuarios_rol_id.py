"""Clave foránea de usuarios.rol_id hacia roles

Revision ID: b7c41e9a2f30
Revises: 27ba4e31f8c6
Create Date: 2026-10-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b7c41e9a2f30'
down_revision: Union[str, None] = '27ba4e31f8c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_usuarios_rol_id', 'roles', ['rol_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('fk_usuarios_rol_id', type_='foreignkey')
