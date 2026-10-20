from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_filename: Mapped[str]
    stored_filename: Mapped[str]
    content_type: Mapped[str]
    size: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus),
        default=DocumentStatus.uploaded,
    )
    error: Mapped[str | None]
    text_data: Mapped["DocumentText | None"] = relationship(
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    versions: Mapped[list["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentVersion.version_number",
    )


class DocumentText(Base):
    __tablename__ = "document_text"

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        primary_key=True,
    )
    text: Mapped[str]
    document: Mapped["Document"] = relationship(
        back_populates="text_data",
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
    )
    version_number: Mapped[int]
    file_path: Mapped[str]
    extracted_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    similarity: Mapped[float] = mapped_column(nullable=True)
    msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    document: Mapped["Document"] = relationship("Document", back_populates="versions")


class DocumentDiff(Base):
    __tablename__ = "document_diffs"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "from_version_id",
            "to_version_id",
            name="uq_document_diff_versions",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
    )
    from_version_id: Mapped[int] = mapped_column(
        ForeignKey(
            "document_versions.id",
            ondelete="CASCADE",
        ),
    )
    to_version_id: Mapped[int] = mapped_column(
        ForeignKey(
            "document_versions.id",
            ondelete="CASCADE",
        ),
    )
    raw_diff: Mapped[str] = mapped_column(Text)
    ai_summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
