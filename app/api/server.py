"""Local REST API server (FastAPI) for VoiceForge Local.

Endpoints:
  GET  /api/v1/health
  GET  /api/v1/voices
  GET  /api/v1/voices/{id}
  POST /api/v1/voices/{id}/synthesize
  DELETE /api/v1/jobs/{id}
  GET  /api/v1/models
  GET  /api/v1/status
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config.settings import get_settings
from app.core.hardware import detect_hardware
from app.core.logging import get_logger
from app.engines.primary import PrimaryEngine
from app.voices.manager import VoicePackManager

logger = get_logger("api")

settings = get_settings()


class TTSRequest(BaseModel):
    voice_id: str
    text: str
    language: str = "en"
    output_format: str = "wav"
    speed: float = 1.0


class TTSResponse(BaseModel):
    success: bool
    audio_url: str | None = None
    request_id: str
    voice_id: str
    duration_seconds: float | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    api_address: str


# Global engine instance
_engine: PrimaryEngine | None = None
_voice_manager: VoicePackManager | None = None


def get_engine() -> PrimaryEngine:
    global _engine
    if _engine is None:
        _engine = PrimaryEngine(model_dir=settings.model_dir)
    return _engine


def get_voice_manager() -> VoicePackManager:
    global _voice_manager
    if _voice_manager is None:
        _voice_manager = VoicePackManager(voice_pack_dir=settings.voice_pack_dir)
    return _voice_manager


def create_app() -> FastAPI:
    app = FastAPI(title="VoiceForge Local API", version="0.1.0")

    @app.get("/api/v1/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version="0.1.0",
            api_address=f"{settings.api_host}:{settings.api_port}",
        )

    @app.get("/api/v1/voices")
    async def list_voices() -> list[dict[str, Any]]:
        return get_voice_manager().list_voice_packs()

    @app.get("/api/v1/voices/{voice_id}")
    async def get_voice(voice_id: str) -> dict[str, Any]:
        schema = get_voice_manager().get_voice_pack(voice_id)
        if schema is None:
            raise HTTPException(status_code=404, detail="Voice pack not found")
        return schema.to_dict()

    @app.post("/api/v1/voices/{voice_id}/synthesize", response_model=TTSResponse)
    async def synthesize(voice_id: str, request: TTSRequest) -> TTSResponse:
        schema = get_voice_manager().get_voice_pack(voice_id)
        if schema is None:
            raise HTTPException(status_code=404, detail="Voice pack not found")

        engine = get_engine()
        voice_profile = {
            "voice_id": voice_id,
            "engine": schema.engine.id,
            "engine_version": schema.engine.version,
            "sample_rate": schema.audio_profile.sample_rate,
            "reference_files": [
                str(Path(settings.voice_pack_dir) / voice_id / "reference_audio" / f)
                for f in schema.speaker.reference_files
            ],
        }

        result = engine.synthesize(
            text=request.text,
            voice_profile=voice_profile,
            options={"language": request.language, "speed": request.speed},
        )

        return TTSResponse(
            success=True,
            audio_url=f"/api/v1/audio/{Path(result.audio_path).name}",
            request_id=result.request_id,
            voice_id=voice_id,
            duration_seconds=result.duration_seconds,
        )

    @app.get("/api/v1/audio/{filename}")
    async def get_audio(filename: str):
        file_path = Path("data/outputs") / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        return FileResponse(str(file_path))

    @app.delete("/api/v1/jobs/{job_id}")
    async def delete_job(job_id: str):
        # Placeholder for job management
        return {"success": True, "job_id": job_id}

    @app.get("/api/v1/models")
    async def list_models() -> list[dict[str, Any]]:
        return [
            {
                "id": "primary",
                "name": "Primary Local TTS",
                "version": "0.1.0",
                "languages": ["en", "hi"],
                "installed": True,
            }
        ]

    @app.get("/api/v1/status")
    async def status() -> dict[str, Any]:
        hw = detect_hardware()
        return {
            "api": "running",
            "engine_loaded": get_engine().is_loaded(),
            "hardware": hw.summary(),
        }

    return app


app = create_app()