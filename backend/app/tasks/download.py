"""
Download task - handles YouTube video downloads using yt-dlp.
"""

import os
import logging
from pathlib import Path
from yt_dlp import YoutubeDL
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.battle import Battle, BattleStatus
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create upload directory if it doesn't exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)


@celery_app.task(bind=True, name="tasks.download_youtube_video")
def download_youtube_video(self, battle_id: int, url: str) -> dict:
    """
    Download audio from YouTube video using yt-dlp.

    Args:
        battle_id: ID of the battle to associate with download
        url: YouTube URL to download

    Returns:
        Dictionary with audio file path and metadata
    """
    def _update(state, meta):
        if self.request.id:
            self.update_state(state=state, meta=meta)

    db = SessionLocal()
    try:
        logger.info(f"Starting download for battle {battle_id}")
        _update('PROCESSING', {'status': 'Downloading from YouTube...'})

        # Update battle status
        battle = db.query(Battle).filter(Battle.id == battle_id).first()
        if not battle:
            raise ValueError(f"Battle {battle_id} not found")

        battle.status = BattleStatus.PROCESSING
        db.commit()

        # Prepare output path
        output_dir = Path(settings.TEMP_DIR) / f"battle_{battle_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_template = str(output_dir / "%(title)s.%(ext)s")

        # Configure yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }
            ],
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
        }

        # Download video
        logger.info(f"Downloading: {url}")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_filename = f"{info['id']}.wav"
            audio_path = output_dir / audio_filename

            if not audio_path.exists():
                # Try to find the file that was created
                wav_files = list(output_dir.glob("*.wav"))
                if wav_files:
                    audio_path = wav_files[0]
                else:
                    raise FileNotFoundError(f"Audio file not found in {output_dir}")

        logger.info(f"Download completed: {audio_path}")

        result = {
            "battle_id": battle_id,
            "audio_path": str(audio_path),
            "video_title": info.get('title'),
            "video_id": info.get('id'),
            "duration": info.get('duration'),
        }

        logger.info(f"Download task completed successfully for battle {battle_id}")
        return result

    except Exception as e:
        logger.error(f"Download task failed for battle {battle_id}: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.save_uploaded_file")
def save_uploaded_file(self, battle_id: int, filename: str, file_content: bytes) -> dict:
    """
    Save uploaded file to disk.

    Args:
        battle_id: ID of the battle
        filename: Original filename
        file_content: File contents as bytes

    Returns:
        Dictionary with saved file path
    """
    try:
        def _update(state, meta):
            if self.request.id:
                self.update_state(state=state, meta=meta)

        logger.info(f"Saving uploaded file for battle {battle_id}: {filename}")
        _update('PROCESSING', {'status': 'Saving file...'})

        # Create directory
        output_dir = Path(settings.TEMP_DIR) / f"battle_{battle_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = output_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)

        logger.info(f"File saved: {file_path}")

        return {
            "battle_id": battle_id,
            "file_path": str(file_path),
            "filename": filename,
        }

    except Exception as e:
        logger.error(f"Failed to save file for battle {battle_id}: {str(e)}", exc_info=True)
        raise
