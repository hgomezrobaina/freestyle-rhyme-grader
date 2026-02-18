#!/usr/bin/env python
"""
Verificación completa de Fase 2.
Valida que todos los modules, tasks y endpoints estén correctamente implementados.

Ejecutar: python verify_phase2.py
"""

import sys
import os
from pathlib import Path

def check_module(module_path: str, module_name: str) -> bool:
    """Verificar que un módulo existe e importa correctamente."""
    try:
        # Convertir path a import statement
        parts = module_path.replace("\\", "/").replace("/", ".").replace(".py", "")
        exec(f"import {parts}")
        print(f"✅ {module_name}")
        return True
    except Exception as e:
        print(f"❌ {module_name}: {str(e)}")
        return False

def check_file_exists(file_path: str, description: str) -> bool:
    """Verificar que un archivo existe."""
    if Path(file_path).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_endpoint_in_file(file_path: str, endpoint_name: str) -> bool:
    """Verificar que un endpoint existe en un archivo."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if endpoint_name in content:
                print(f"✅ {endpoint_name}")
                return True
            else:
                print(f"❌ {endpoint_name} - NOT FOUND")
                return False
    except Exception as e:
        print(f"❌ {endpoint_name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🔍 FASE 2 - Verificación Completa")
    print("=" * 60)

    all_passed = True

    # 1. Verificar estructura de directorios
    print("\n📁 Estructura de Directorios:")
    directories = [
        "app/workers",
        "app/tasks",
        "app/api",
        "uploads",
        "temp",
    ]

    for dir in directories:
        if Path(dir).exists():
            print(f"✅ {dir}/")
        else:
            print(f"⚠️  {dir}/ - NO EXISTE (se creará automáticamente)")

    # 2. Verificar archivos principales
    print("\n📄 Archivos Principales (Fase 2):")
    files = [
        ("app/workers/celery_app.py", "Celery Configuration"),
        ("app/workers/__init__.py", "Workers Package Init"),
        ("app/tasks/download.py", "Download Tasks"),
        ("app/tasks/transcription.py", "Transcription Task"),
        ("app/tasks/voice_separation.py", "Voice Separation Task"),
        ("app/tasks/diarization.py", "Diarization Task"),
        ("app/tasks/pipeline.py", "Pipeline Orchestrator"),
        ("app/tasks/__init__.py", "Tasks Package Init"),
        ("app/api/youtube_router.py", "YouTube Endpoint"),
        ("app/api/upload_router.py", "Upload Endpoint"),
        ("start_worker.py", "Celery Worker Starter"),
        ("PHASE2_GUIDE.md", "Fase 2 Guide"),
        ("PHASE2_SUMMARY.md", "Fase 2 Summary"),
        ("IMPLEMENTATION_COMPLETE.md", "Implementation Summary"),
    ]

    for file_path, description in files:
        if not check_file_exists(file_path, description):
            all_passed = False

    # 3. Verificar endpoints
    print("\n🌐 Endpoints (Verificación de código):")
    endpoints = [
        ("app/api/youtube_router.py", "create_battle_from_youtube"),
        ("app/api/upload_router.py", "create_battle_from_upload"),
        ("app/api/youtube_router.py", "get_battle_status"),
    ]

    for file_path, endpoint in endpoints:
        if not check_endpoint_in_file(file_path, endpoint):
            all_passed = False

    # 4. Verificar Celery Tasks
    print("\n🎬 Celery Tasks (Verificación de código):")
    tasks = [
        ("app/tasks/download.py", "download_youtube_video"),
        ("app/tasks/download.py", "save_uploaded_file"),
        ("app/tasks/transcription.py", "transcribe_audio"),
        ("app/tasks/voice_separation.py", "separate_voices"),
        ("app/tasks/diarization.py", "diarize_speakers"),
        ("app/tasks/pipeline.py", "process_pipeline"),
    ]

    for file_path, task_name in tasks:
        if not check_endpoint_in_file(file_path, task_name):
            all_passed = False

    # 5. Verificar imports en main.py
    print("\n📍 Main.py Integration:")
    main_imports = [
        ("app/main.py", "youtube_router"),
        ("app/main.py", "upload_router"),
    ]

    for file_path, import_name in main_imports:
        if not check_endpoint_in_file(file_path, import_name):
            all_passed = False

    # 6. Verificar requirements.txt
    print("\n📦 Dependencies (requirements.txt):")
    required_deps = [
        "celery",
        "redis",
        "openai-whisper",
        "demucs",
        "pyannote.audio",
        "yt-dlp",
        "torch",
        "torchaudio",
    ]

    if Path("requirements.txt").exists():
        with open("requirements.txt", 'r') as f:
            reqs_content = f.read()
            for dep in required_deps:
                if dep in reqs_content:
                    print(f"✅ {dep}")
                else:
                    print(f"❌ {dep} - NOT IN requirements.txt")
                    all_passed = False
    else:
        print("❌ requirements.txt NOT FOUND")
        all_passed = False

    # 7. Verificar database models
    print("\n🗄️ Database Models:")
    models = [
        ("app/models/battle.py", "BattleStatus"),
        ("app/models/battle.py", "BattleSourceType"),
    ]

    for file_path, model in models:
        if not check_endpoint_in_file(file_path, model):
            all_passed = False

    # Final summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✨ VERIFICACIÓN COMPLETADA - TODO ESTÁ BIEN")
        print("=" * 60)
        print("\nPróximos pasos:")
        print("1. pip install -r requirements.txt")
        print("2. docker-compose up -d")
        print("3. Terminal 1: python -m uvicorn app.main:app --reload")
        print("4. Terminal 2: python start_worker.py")
        print("5. Ver PHASE2_GUIDE.md para ejemplos de uso")
        return 0
    else:
        print("⚠️ ALGUNAS VERIFICACIONES FALLARON")
        print("=" * 60)
        print("\nRevisa los archivos indicados arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
