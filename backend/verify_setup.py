#!/usr/bin/env python
"""
Verification script to check if all dependencies are installed correctly.
Run this after: pip install -r requirements.txt
"""

import sys
from pathlib import Path

def check_import(module_name: str, friendly_name: str = None) -> bool:
    """Try to import a module and report status."""
    name = friendly_name or module_name
    try:
        __import__(module_name)
        print(f"✅ {name}")
        return True
    except ImportError as e:
        print(f"❌ {name}: {e}")
        return False

def check_folder(folder_path: str) -> bool:
    """Check if a folder exists."""
    p = Path(folder_path)
    if p.exists() and p.is_dir():
        print(f"✅ Folder: {folder_path}")
        return True
    else:
        print(f"❌ Folder missing: {folder_path}")
        return False

def main():
    print("=" * 60)
    print("🔍 Freestyle Callificator - Dependency Verification")
    print("=" * 60)

    all_checks_passed = True

    # Check Python version
    print("\n📦 System Requirements:")
    py_version = sys.version_info
    if py_version.major == 3 and py_version.minor >= 10:
        print(f"✅ Python {py_version.major}.{py_version.minor}+")
    else:
        print(f"❌ Python 3.10+ required (you have {py_version.major}.{py_version.minor})")
        all_checks_passed = False

    # Check core dependencies
    print("\n🔧 Core Dependencies:")
    core_deps = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("psycopg2", "PostgreSQL Driver"),
        ("pydantic", "Pydantic"),
        ("uvicorn", "Uvicorn"),
    ]

    for module, name in core_deps:
        if not check_import(module, name):
            all_checks_passed = False

    # Check analysis dependencies
    print("\n🧠 Analysis Dependencies:")
    analysis_deps = [
        ("phonemizer", "Phonemizer (IPA)"),
        ("pyphen", "Pyphen (Syllables)"),
        ("librosa", "Librosa (Audio)"),
    ]

    for module, name in analysis_deps:
        if not check_import(module, name):
            all_checks_passed = False

    # Check optional (future) dependencies
    print("\n🔄 Optional (Future Phases):")
    optional_deps = [
        ("celery", "Celery"),
        ("redis", "Redis Python"),
        ("whisper", "OpenAI Whisper"),
        ("yt_dlp", "yt-dlp"),
    ]

    for module, name in optional_deps:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"⏳ {name} (optional - needed for Phase 2)")

    # Check folder structure
    print("\n📁 Project Structure:")
    folders = [
        "app",
        "app/api",
        "app/models",
        "app/services",
        "app/tasks",
        "analysis",
        "analysis/phonetic",
        "analysis/rhyme",
        "workers",
    ]

    for folder in folders:
        if not check_folder(folder):
            all_checks_passed = False

    # Check key files
    print("\n📄 Key Files:")
    files = [
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "requirements.txt",
        "docker-compose.yml",
        ".env",
        "README.md",
        "QUICKSTART.md",
        "example_usage.py",
    ]

    for file in files:
        p = Path(file)
        if p.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ Missing: {file}")
            all_checks_passed = False

    # Check environment
    print("\n⚙️ Environment Configuration:")
    try:
        from app.config import get_settings
        settings = get_settings()
        print(f"✅ Config loaded")
        print(f"   - Database: {settings.DATABASE_URL[:30]}...")
        print(f"   - Redis: {settings.REDIS_URL}")
        print(f"   - Debug: {settings.DEBUG}")
    except Exception as e:
        print(f"⚠️ Config warning: {e}")

    # Final summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✨ All checks passed! Ready to go.")
        print("\nNext steps:")
        print("1. docker-compose up -d")
        print("2. python -m uvicorn app.main:app --reload")
        print("3. Open http://localhost:8000/docs")
        print("4. Run 'python example_usage.py' to test")
        return 0
    else:
        print("⚠️ Some checks failed. See above for details.")
        print("\nCommon fixes:")
        print("- Install: pip install -r requirements.txt")
        print("- System espeak: brew install espeak-ng (macOS)")
        print("- System espeak: sudo apt install espeak-ng (Linux)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
