from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from server.app.database import Base


class Audio(Base):
    __tablename__ = "audios"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    original_name: Mapped[str] = mapped_column(String, nullable=False)
    original_ext: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    sample_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channels: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bitrate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    processing_type: Mapped[str] = mapped_column(String, nullable=False, default="original")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    path_original: Mapped[str] = mapped_column(Text, nullable=False)
    path_processed: Mapped[str | None] = mapped_column(Text, nullable=True)
