"""
Transcription task - handles audio transcription using OpenAI Whisper.
"""

import logging
from pathlib import Path
import whisper
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.battle import Battle

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.transcribe_audio")
def transcribe_audio(self, battle_id: int, audio_path: str) -> dict:
    """
    Transcribe audio file using Whisper.

    Args:
        battle_id: ID of the battle
        audio_path: Path to audio file

    Returns:
        Dictionary with transcription and segments
    """
    def _update(state, meta):
        if self.request.id:
            self.update_state(state=state, meta=meta)

    db = SessionLocal()
    try:
        logger.info(f"Starting transcription for battle {battle_id}")
        _update('PROCESSING', {'status': 'Transcribing audio...'})

        # Verify file exists
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load Whisper model
        logger.info("Loading Whisper model (large-v3)...")
        _update('PROCESSING', {'status': 'Loading Whisper model...'})
        model = whisper.load_model("large-v3")

        # Transcribe
        logger.info(f"Transcribing: {audio_path}")
        _update('PROCESSING', {'status': 'Transcribing audio (this may take a few minutes)...'})
        result = model.transcribe(audio_path, language="es")

        logger.info(f"Transcription completed")

        # Extract text and segments
        full_text = result.get("text", "")
        segments = result.get("segments", [])

        # Process segments
        segment_list = []
        for seg in segments:
            segment_list.append({
                "start_time": seg.get("start"),
                "end_time": seg.get("end"),
                "text": seg.get("text", "").strip(),
                "id": seg.get("id"),
            })

        logger.info(f"Found {len(segment_list)} segments")

        result_data = {
            "battle_id": battle_id,
            "full_text": full_text,
            "segments": segment_list,
            "language": result.get("language"),
        }

        logger.info(f"Transcription task completed for battle {battle_id}")
        return result_data

    except Exception as e:
        logger.error(f"Transcription failed for battle {battle_id}: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()
