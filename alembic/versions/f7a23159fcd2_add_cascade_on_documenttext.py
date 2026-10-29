"""add cascade on documenttext

Revision ID: f7a23159fcd2
Revises: 8d2a5e23e942
Create Date: 2026-10-29 11:53:33.753932

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f7a23159fcd2"
down_revision: str | Sequence[str] | None = "8d2a5e23e942"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        op.f("document_text_document_id_fkey"),
        "document_text",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("document_text_document_id_fkey"),
        "document_text",
        "documents",
        ["document_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("document_text_document_id_fkey"),
        "document_text",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("document_text_document_id_fkey"),
        "document_text",
        "documents",
        ["document_id"],
        ["id"],
    )
