"""Hardware detection for CPU, GPU, CUDA, VRAM, and FFmpeg."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HardwareInfo:
    """Detected hardware capabilities."""

    cpu_count: int = 0
    cpu_brand: str = "Unknown"
    ram_total_gb: float = 0.0
    gpu_detected: bool = False
    gpu_name: str = "None"
    vram_total_gb: float = 0.0
    cuda_available: bool = False
    cuda_version: str = ""
    torch_version: str = ""
    ffmpeg_available: bool = False
    ffmpeg_version: str = ""
    model_available: bool = False

    def summary(self) -> dict[str, Any]:
        return {
            "cpu": {
                "count": self.cpu_count,
                "brand": self.cpu_brand,
            },
            "ram_gb": round(self.ram_total_gb, 1),
            "gpu": {
                "detected": self.gpu_detected,
                "name": self.gpu_name,
                "vram_gb": round(self.vram_total_gb, 1),
            },
            "cuda": {
                "available": self.cuda_available,
                "version": self.cuda_version,
            },
            "torch": self.torch_version,
            "ffmpeg": {
                "available": self.ffmpeg_available,
                "version": self.ffmpeg_version,
            },
            "model_available": self.model_available,
        }


def detect_ffmpeg() -> tuple[bool, str]:
    """Check if FFmpeg is available and return version string."""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        return False, ""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            first_line = result.stdout.splitlines()[0] if result.stdout else ""
            return True, first_line
    except Exception:
        pass
    return False, ""


def detect_hardware() -> HardwareInfo:
    """Detect all available hardware and return a HardwareInfo object."""
    import psutil

    info = HardwareInfo()

    # CPU
    try:
        info.cpu_count = psutil.cpu_count(logical=True) or 0
    except Exception:
        info.cpu_count = 0

    try:
        info.cpu_brand = platform_cpu_brand()
    except Exception:
        info.cpu_brand = "Unknown"

    # RAM
    try:
        mem = psutil.virtual_memory()
        info.ram_total_gb = round(mem.total / (1024**3), 1)
    except Exception:
        info.ram_total_gb = 0.0

    # FFmpeg
    ffmpeg_ok, ffmpeg_ver = detect_ffmpeg()
    info.ffmpeg_available = ffmpeg_ok
    info.ffmpeg_version = ffmpeg_ver

    # PyTorch / CUDA / GPU
    try:
        import torch

        info.torch_version = torch.__version__
        info.cuda_available = bool(torch.cuda.is_available())
        if info.cuda_available:
            try:
                info.cuda_version = torch.version.cuda or ""
                device_count = torch.cuda.device_count()
                if device_count > 0:
                    info.gpu_detected = True
                    info.gpu_name = torch.cuda.get_device_name(0)
                    props = torch.cuda.get_device_properties(0)
                    info.vram_total_gb = round(props.total_memory / (1024**3), 1)
            except Exception:
                pass
    except ImportError:
        info.torch_version = "not installed"

    return info


def platform_cpu_brand() -> str:
    """Attempt to get a human-readable CPU brand string."""
    import platform

    system = platform.system()
    if system == "Windows":
        try:
            import subprocess

            result = subprocess.run(
                ["wmic", "cpu", "get", "name"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            if len(lines) > 1:
                return lines[1]
        except Exception:
            pass
    return platform.processor() or "Unknown CPU"


def format_hardware_summary(info: HardwareInfo) -> str:
    """Return a human-readable hardware summary string."""
    lines = [
        f"CPU: {info.cpu_brand} ({info.cpu_count} cores)",
        f"RAM: {info.ram_total_gb} GB",
    ]
    if info.gpu_detected:
        lines.append(f"GPU: {info.gpu_name} ({info.vram_total_gb} GB VRAM)")
    else:
        lines.append("GPU: None detected")
    lines.append(f"CUDA: {'Available' if info.cuda_available else 'Not available'}")
    lines.append(f"PyTorch: {info.torch_version}")
    lines.append(f"FFmpeg: {'Installed' if info.ffmpeg_available else 'Missing'}")
    return "\n".join(lines)