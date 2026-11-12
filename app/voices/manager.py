"""Voice pack manager - create, load, save, export, import voice packs."""

from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config.settings import get_settings
from app.core.logging import get_logger
from app.voices.schema import VoicePackSchema, AuthorizationRecord

logger = get_logger("voices")


class VoicePackManager:
    """Manages voice packs on disk - CRUD, import, export."""

    def __init__(self, voice_pack_dir: Path | str | None = None) -> None:
        settings = get_settings()
        self.voice_pack_dir = Path(voice_pack_dir) if voice_pack_dir else settings.voice_pack_dir
        self.voice_pack_dir.mkdir(parents=True, exist_ok=True)

    def _pack_dir(self, voice_id: str) -> Path:
        return self.voice_pack_dir / voice_id

    def list_voice_packs(self) -> list[dict]:
        """List all voice packs with basic metadata."""
        packs: list[dict] = []
        if not self.voice_pack_dir.exists():
            return packs

        for entry in sorted(self.voice_pack_dir.iterdir()):
            if not entry.is_dir():
                continue
            meta_path = entry / "voicepack.json"
            if not meta_path.exists():
                continue
            try:
                schema = VoicePackSchema.from_json(meta_path.read_text(encoding="utf-8"))
                packs.append(
                    {
                        "id": schema.id,
                        "name": schema.name,
                        "display_name": schema.display_name,
                        "language": schema.language,
                        "engine": schema.engine.id,
                        "created_at": schema.created_at,
                        "updated_at": schema.updated_at,
                        "authorization_confirmed": schema.authorization.confirmed,
                        "path": str(entry),
                    }
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed to read voice pack %s: %s", entry.name, exc)
        return packs

    def get_voice_pack(self, voice_id: str) -> Optional[VoicePackSchema]:
        """Load a voice pack schema by ID."""
        meta_path = self._pack_dir(voice_id) / "voicepack.json"
        if not meta_path.exists():
            return None
        return VoicePackSchema.from_json(meta_path.read_text(encoding="utf-8"))

    def create_voice_pack(self, schema: VoicePackSchema) -> Path:
        """Create a new voice pack directory and write metadata."""
        pack_dir = self._pack_dir(schema.id)
        if pack_dir.exists():
            raise FileExistsError(f"Voice pack already exists: {schema.id}")

        pack_dir.mkdir(parents=True, exist_ok=True)
        (pack_dir / "reference_audio").mkdir(exist_ok=True)
        (pack_dir / "preview").mkdir(exist_ok=True)
        (pack_dir / "metadata").mkdir(exist_ok=True)
        (pack_dir / "engine").mkdir(exist_ok=True)

        meta_path = pack_dir / "voicepack.json"
        meta_path.write_text(schema.to_json(), encoding="utf-8")

        logger.info("Created voice pack: %s at %s", schema.id, pack_dir)
        return pack_dir

    def update_voice_pack(self, schema: VoicePackSchema) -> None:
        """Update an existing voice pack's metadata."""
        pack_dir = self._pack_dir(schema.id)
        if not pack_dir.exists():
            raise FileNotFoundError(f"Voice pack not found: {schema.id}")

        schema.updated_at = datetime.now(timezone.utc).isoformat()
        meta_path = pack_dir / "voicepack.json"
        meta_path.write_text(schema.to_json(), encoding="utf-8")

        logger.info("Updated voice pack: %s", schema.id)

    def delete_voice_pack(self, voice_id: str, delete_files: bool = True) -> None:
        """Delete a voice pack and optionally its files."""
        pack_dir = self._pack_dir(voice_id)
        if not pack_dir.exists():
            raise FileNotFoundError(f"Voice pack not found: {voice_id}")

        if delete_files:
            shutil.rmtree(pack_dir)
        else:
            meta_path = pack_dir / "voicepack.json"
            if meta_path.exists():
                meta_path.unlink()

        logger.info("Deleted voice pack: %s", voice_id)

    def export_voice_pack(self, voice_id: str, output_path: Path) -> Path:
        """Export a voice pack as a .voicepack ZIP file."""
        pack_dir = self._pack_dir(voice_id)
        if not pack_dir.exists():
            raise FileNotFoundError(f"Voice pack not found: {voice_id}")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in pack_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(pack_dir)
                    zf.write(file_path, arcname)

        logger.info("Exported voice pack %s to %s", voice_id, output_path)
        return output_path

    def import_voice_pack(self, zip_path: Path) -> VoicePackSchema:
        """Import a voice pack from a .voicepack ZIP file."""
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise FileNotFoundError(f"Zip file not found: {zip_path}")

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            for name in names:
                if ".." in name or name.startswith("/"):
                    raise ValueError(f"Unsafe path in voice pack: {name}")

            if "voicepack.json" not in names:
                raise ValueError("Invalid voice pack: missing voicepack.json")

            schema = VoicePackSchema.from_json(
                zf.read("voicepack.json").decode("utf-8")
            )

        errors = schema.validate()
        if errors:
            raise ValueError(f"Invalid voice pack: {'; '.join(errors)}")

        pack_dir = self._pack_dir(schema.id)
        if pack_dir.exists():
            raise FileExistsError(f"Voice pack already exists: {schema.id}")

        pack_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(pack_dir)

        logger.info("Imported voice pack: %s from %s", schema.id, zip_path)
        return schema

    def add_reference_audio(
        self, voice_id: str, source_path: Path, dest_name: str | None = None
    ) -> Path:
        """Copy a reference audio file into a voice pack."""
        pack_dir = self._pack_dir(voice_id)
        if not pack_dir.exists():
            raise FileNotFoundError(f"Voice pack not found: {voice_id}")

        ref_dir = pack_dir / "reference_audio"
        ref_dir.mkdir(exist_ok=True)

        dest_name = dest_name or source_path.name
        dest_path = ref_dir / dest_name
        shutil.copy2(source_path, dest_path)

        logger.info("Added reference audio to %s: %s", voice_id, dest_path)
        return dest_path

    def add_preview_audio(self, voice_id: str, source_path: Path) -> Path:
        """Copy a preview audio file into a voice pack."""
        pack_dir = self._pack_dir(voice_id)
        if not pack_dir.exists():
            raise FileNotFoundError(f"Voice pack not found: {voice_id}")

        preview_dir = pack_dir / "preview"
        preview_dir.mkdir(exist_ok=True)

        dest_path = preview_dir / "preview.wav"
        shutil.copy2(source_path, dest_path)

        logger.info("Added preview audio to %s", voice_id)
        return dest_path

    def save_embedding(self, voice_id: str, embedding_data: bytes) -> Path:
        """Save speaker embedding binary to a voice pack."""
        pack_dir = self._pack_dir(voice_id)
        if not pack_dir.exists():
            raise FileNotFoundError(f"Voice pack not found: {voice_id}")

        embedding_path = pack_dir / "speaker_embedding.bin"
        embedding_path.write_bytes(embedding_data)

        logger.info("Saved embedding for %s", voice_id)
        return embedding_path

    def set_authorization(
        self, voice_id: str, confirmed: bool, confirmation_text: str
    ) -> None:
        """Set authorization record on a voice pack."""
        schema = self.get_voice_pack(voice_id)
        if schema is None:
            raise FileNotFoundError(f"Voice pack not found: {voice_id}")

        schema.authorization = AuthorizationRecord(
            confirmed=confirmed,
            confirmation_text=confirmation_text,
            confirmed_at=datetime.now(timezone.utc).isoformat(),
        )
        self.update_voice_pack(schema)