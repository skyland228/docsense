"""add cascade delete to document_text

Revision ID: 377dd848148e
Revises: 50b99de07b6a
Create Date: 2026-10-08 09:40:19.613449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '377dd848148e'
down_revision: Union[str, Sequence[str], None] = '50b99de07b6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        'document_text_document_id_fkey',
        'document_text',
        type_='foreignkey',
    )
    op.create_foreign_key(
        'document_text_document_id_fkey',
        'document_text',
        'documents',
        ['document_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'document_text_document_id_fkey',
        'document_text',
        type_='foreignkey',
    )
    op.create_foreign_key(
        'document_text_document_id_fkey',
        'document_text',
        'documents',
        ['document_id'],
        ['id'],
    )
