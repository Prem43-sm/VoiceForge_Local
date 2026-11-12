"""SQLAlchemy ORM models for VoiceForge Local."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class VoicePack(Base):
    """Indexed record of a voice pack on disk."""

    __tablename__ = "voices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(32), default="en")
    engine_id: Mapped[str] = mapped_column(String(64), default="primary")
    model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    sample_rate: Mapped[int] = mapped_column(Integer, default=24000)
    channels: Mapped[int] = mapped_column(Integer, default=1)
    authorization_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    authorization_confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    voice_pack_path: Mapped[str] = mapped_column(String(512))
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    jobs: Mapped[list["SynthesisJob"]] = relationship(
        "SynthesisJob", back_populates="voice_pack", cascade="all, delete-orphan"
    )


class ModelRecord(Base):
    """Installed model record."""

    __tablename__ = "models"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(64))
    license: Mapped[str] = mapped_column(String(128))
    languages: Mapped[str] = mapped_column(String(128), default="en")
    size_mb: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    vram_recommendation_gb: Mapped[Optional[float]] = mapped_column(
        Integer, nullable=True
    )
    installed: Mapped[bool] = mapped_column(Boolean, default=False)
    install_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class SynthesisJob(Base):
    """Background synthesis job record."""

    __tablename__ = "synthesis_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    voice_id: Mapped[str] = mapped_column(ForeignKey("voices.id"))
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(32), default="en")
    output_format: Mapped[str] = mapped_column(String(16), default="wav")
    output_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="QUEUED")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    voice_pack: Mapped["VoicePack"] = relationship("VoicePack", back_populates="jobs")


class Setting(Base):
    """Key-value application settings."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class LogEntry(Base):
    """Application log entries stored in DB."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(Text)
    module: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)