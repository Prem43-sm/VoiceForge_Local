"""CLI for VoiceForge Local.

Commands:
  voiceforge list-voices
  voiceforge create-voice
  voiceforge analyze-audio <file>
  voiceforge test --voice <id> --text <text> --output <file>
  voiceforge speak --voice <id> --text <text> --output <file>
  voiceforge export <voice-id> <output.zip>
  voiceforge import <zip-file>
  voiceforge models
  voiceforge doctor
  voiceforge server
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.api.server import create_app
from app.config.settings import get_settings
from app.core.hardware import detect_hardware, format_hardware_summary
from app.core.logging import setup_logging, get_logger
from app.database.connection import init_db
from app.voices.manager import VoicePackManager

logger = get_logger("cli")


def cmd_list_voices(args: argparse.Namespace) -> int:
    settings = get_settings()
    vm = VoicePackManager(settings.voice_pack_dir)
    packs = vm.list_voice_packs()
    if not packs:
        print("No voice packs found.")
        return 0
    print(f"{'ID':<12} {'Name':<30} {'Lang':<8} {'Engine':<12} {'Auth':<6}")
    print("-" * 70)
    for p in packs:
        auth = "yes" if p.get("authorization_confirmed") else "no"
        lang = p.get("language", ["?"])
        lang_str = lang[0] if lang else "?"
        print(f"{p['id']:<12} {p.get('display_name', p.get('name', '')):<30} "
              f"{lang_str:<8} {p.get('engine', '?'):<12} {auth:<6}")
    return 0


def cmd_analyze_audio(args: argparse.Namespace) -> int:
    from app.audio.analysis import AudioAnalyzer

    analyzer = AudioAnalyzer()
    report = analyzer.analyze(args.file)
    print(f"File: {report.file_path}")
    print(f"Duration: {report.duration:.2f}s")
    print(f"Sample rate: {report.sample_rate} Hz")
    print(f"Channels: {report.channels}")
    print(f"RMS loudness: {report.rms_loudness:.4f}")
    print(f"Peak level: {report.peak_level:.4f}")
    print(f"Clipping: {report.clipping}")
    print(f"Silence ratio: {report.silence_ratio:.2%}")
    print(f"Speech ratio: {report.speech_ratio:.2%}")
    print(f"Quality score: {report.quality_score}/100 ({report.quality_label})")
    if report.issues:
        print("Issues:")
        for issue in report.issues:
            print(f"  - {issue}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    settings = get_settings()
    vm = VoicePackManager(settings.voice_pack_dir)
    schema = vm.get_voice_pack(args.voice)
    if schema is None:
        print(f"Voice pack not found: {args.voice}")
        return 1

    from app.engines.primary import PrimaryEngine

    engine = PrimaryEngine(model_dir=settings.model_dir)
    voice_profile = {
        "voice_id": args.voice,
        "engine": schema.engine.id,
        "sample_rate": schema.audio_profile.sample_rate,
        "reference_files": schema.speaker.reference_files,
    }

    result = engine.synthesize(
        text=args.text,
        voice_profile=voice_profile,
        options={"language": args.language},
    )

    print(f"Generated: {result.audio_path}")
    print(f"Duration: {result.duration_seconds:.1f}s")
    print(f"RTF: {result.rtf:.2f}")

    if args.output:
        import shutil
        shutil.copy2(result.audio_path, args.output)
        print(f"Copied to: {args.output}")
    return 0


def cmd_speak(args: argparse.Namespace) -> int:
    return cmd_test(args)


def cmd_export(args: argparse.Namespace) -> int:
    settings = get_settings()
    vm = VoicePackManager(settings.voice_pack_dir)
    output_path = vm.export_voice_pack(args.voice_id, Path(args.output))
    print(f"Exported to: {output_path}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    settings = get_settings()
    vm = VoicePackManager(settings.voice_pack_dir)
    schema = vm.import_voice_pack(Path(args.zip_file))
    print(f"Imported voice pack: {schema.id} ({schema.display_name})")
    return 0


def cmd_models(args: argparse.Namespace) -> int:
    print("Available models:")
    print("  primary - Primary Local TTS (en, hi) - placeholder")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    print("VoiceForge Local - Doctor Diagnostics")
    print("=" * 40)

    settings = get_settings()
    print(f"Python: {sys.version.split()[0]}")

    hw = detect_hardware()
    print(format_hardware_summary(hw))

    print()
    print("Directories:")
    for name, path in [
        ("models", settings.model_dir),
        ("voice_packs", settings.voice_pack_dir),
        ("outputs", settings.output_dir),
        ("cache", settings.cache_dir),
        ("logs", settings.log_dir),
    ]:
        exists = Path(path).exists()
        print(f"  {name}: {path} ({'OK' if exists else 'MISSING'})")

    try:
        init_db(settings.db_path)
        print(f"  database: {settings.db_path} (OK)")
    except Exception as exc:
        print(f"  database: {settings.db_path} (FAIL: {exc})")

    print()
    print("Doctor check complete.")
    return 0


def cmd_server(args: argparse.Namespace) -> int:
    import uvicorn

    settings = get_settings()
    print(f"Starting VoiceForge Local API on {settings.api_host}:{settings.api_port}")
    print("API docs: http://127.0.0.1:8765/docs")
    print("Press Ctrl+C to stop.")
    uvicorn.run(
        create_app(),
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="voiceforge", description="VoiceForge Local CLI")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    sub.add_parser("list-voices", help="List all voice packs").set_defaults(func=cmd_list_voices)

    p = sub.add_parser("analyze-audio", help="Analyze an audio file")
    p.add_argument("file", help="Path to audio file")
    p.set_defaults(func=cmd_analyze_audio)

    p = sub.add_parser("test", help="Test a voice pack by synthesizing text")
    p.add_argument("--voice", required=True, help="Voice pack ID")
    p.add_argument("--text", required=True, help="Text to synthesize")
    p.add_argument("--language", default="en", help="Language code (default: en)")
    p.add_argument("--output", help="Output WAV file path")
    p.set_defaults(func=cmd_test)

    p = sub.add_parser("speak", help="Alias for test")
    p.add_argument("--voice", required=True, help="Voice pack ID")
    p.add_argument("--text", required=True, help="Text to synthesize")
    p.add_argument("--language", default="en", help="Language code (default: en)")
    p.add_argument("--output", help="Output WAV file path")
    p.set_defaults(func=cmd_speak)

    p = sub.add_parser("export", help="Export a voice pack to .voicepack ZIP")
    p.add_argument("voice_id", help="Voice pack ID to export")
    p.add_argument("output", help="Output ZIP file path")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("import", help="Import a .voicepack ZIP file")
    p.add_argument("zip_file", help="Path to .voicepack ZIP file")
    p.set_defaults(func=cmd_import)

    sub.add_parser("models", help="List available models").set_defaults(func=cmd_models)
    sub.add_parser("doctor", help="Run diagnostics").set_defaults(func=cmd_doctor)
    sub.add_parser("server", help="Start the local API server").set_defaults(func=cmd_server)

    return parser


def main() -> int:
    setup_logging()
    settings = get_settings()
    init_db(settings.db_path)

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())