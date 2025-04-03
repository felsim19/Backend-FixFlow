"""Añadir campo de verifiedMail

Revision ID: 558a30d94b19
Revises: 
Create Date: 2025-04-03 16:42:59.527668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '558a30d94b19'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Primero añade la columna como nullable
    op.add_column('company', sa.Column('verifiedMail', sa.Boolean(), nullable=True))
    
    # 2. Establece valor por defecto para registros existentes
    op.execute("UPDATE company SET verifiedMail = FALSE WHERE verifiedMail IS NULL")
    
    # 3. Cambia a NOT NULL especificando el tipo existente
    op.alter_column(
        'company', 
        'verifiedMail', 
        existing_type=sa.Boolean(),  # ¡Este parámetro es crucial!
        nullable=False
    )

def downgrade() -> None:
    # Para el rollback simplemente eliminamos la columna
    op.drop_column('company', 'verifiedMail')
