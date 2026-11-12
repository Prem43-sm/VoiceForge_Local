"""Voice pack JSON schema definition and validation."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VOICEPACK_VERSION = "1.0"


@dataclass
class AuthorizationRecord:
    confirmed: bool = False
    confirmation_text: str = ""
    confirmed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SpeakerInfo:
    embedding_file: str = "speaker_embedding.bin"
    reference_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AudioProfile:
    sample_rate: int = 24000
    channels: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PreprocessingConfig:
    noise_reduction: bool = True
    silence_trim: bool = True
    normalization: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EngineConfig:
    id: str = "primary"
    version: str = "0.1.0"
    model_id: str = ""
    model_revision: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VoicePackSchema:
    """Stable schema for a voice pack."""

    voicepack_version: str = VOICEPACK_VERSION
    id: str = field(default_factory=lambda: f"vf_{uuid.uuid4().hex[:8]}")
    name: str = ""
    display_name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    language: list[str] = field(default_factory=lambda: ["en"])
    engine: EngineConfig = field(default_factory=EngineConfig)
    speaker: SpeakerInfo = field(default_factory=SpeakerInfo)
    audio_profile: AudioProfile = field(default_factory=AudioProfile)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    authorization: AuthorizationRecord = field(default_factory=AuthorizationRecord)

    def to_dict(self) -> dict[str, Any]:
        return {
            "voicepack_version": self.voicepack_version,
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "language": self.language,
            "engine": self.engine.to_dict(),
            "speaker": self.speaker.to_dict(),
            "audio_profile": self.audio_profile.to_dict(),
            "preprocessing": self.preprocessing.to_dict(),
            "authorization": self.authorization.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VoicePackSchema":
        engine = EngineConfig(**data.get("engine", {}))
        speaker = SpeakerInfo(**data.get("speaker", {}))
        audio_profile = AudioProfile(**data.get("audio_profile", {}))
        preprocessing = PreprocessingConfig(**data.get("preprocessing", {}))
        authorization = AuthorizationRecord(**data.get("authorization", {}))
        return cls(
            voicepack_version=data.get("voicepack_version", VOICEPACK_VERSION),
            id=data.get("id", f"vf_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", ""),
            display_name=data.get("display_name", ""),
            created_at=data.get(
                "created_at", datetime.now(timezone.utc).isoformat()
            ),
            updated_at=data.get(
                "updated_at", datetime.now(timezone.utc).isoformat()
            ),
            language=data.get("language", ["en"]),
            engine=engine,
            speaker=speaker,
            audio_profile=audio_profile,
            preprocessing=preprocessing,
            authorization=authorization,
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "VoicePackSchema":
        return cls.from_dict(json.loads(json_str))

    def validate(self) -> list[str]:
        """Validate the schema and return a list of error messages (empty if valid)."""
        errors: list[str] = []
        if not self.id:
            errors.append("voice pack id is required")
        if not self.name:
            errors.append("voice pack name is required")
        if not self.engine.id:
            errors.append("engine id is required")
        if not self.authorization.confirmed:
            errors.append("authorization must be confirmed")
        if not self.speaker.reference_files:
            errors.append("at least one reference audio file is required")
        return errors

    def compute_file_checksum(self, file_path: Path) -> str:
        """Compute SHA-256 checksum of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()