
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class DocumentStatus(str, Enum):
    uploaded = 'uploaded'
    processing = 'processing'
    ready = 'ready'
    failed = 'failed'


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    original_filename: Mapped[str]
    stored_filename: Mapped[str]
    content_type: Mapped[str]
    size: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus),
        default=DocumentStatus.uploaded,
    )
    error: Mapped[str | None]
    text_data: Mapped['DocumentText | None'] = relationship(
        back_populates='document',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True,
    )


class DocumentText(Base):
    __tablename__ = 'document_text'

    document_id: Mapped[int] = mapped_column(
        ForeignKey('documents.id'),
        primary_key=True,
    )
    text: Mapped[str]
    document: Mapped['Document'] = relationship(
        back_populates='text_data',
    )
