"""
Diarization task - handles speaker identification and segmentation using Pyannote.
"""

import logging
from pathlib import Path
from pyannote.audio import Pipeline
import torch
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.battle import Battle

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.diarize_speakers")
def diarize_speakers(self, battle_id: int, audio_path: str) -> dict:
    """
    Identify and segment speakers in audio using Pyannote.

    Args:
        battle_id: ID of the battle
        audio_path: Path to audio file

    Returns:
        Dictionary with speaker segments and timeline
    """
    def _update(state, meta):
        if self.request.id:
            self.update_state(state=state, meta=meta)

    db = SessionLocal()
    try:
        logger.info(f"Starting diarization for battle {battle_id}")
        _update('PROCESSING', {'status': 'Identifying speakers...'})

        # Verify file exists
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")

        # Load pipeline
        logger.info("Loading Pyannote pipeline...")
        _update('PROCESSING', {'status': 'Loading speaker diarization model...'})

        try:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.0",
                use_auth_token=None  # Set your HF token if needed
            )
            pipeline = pipeline.to(device)
        except Exception as e:
            logger.warning(f"Could not load pyannote pipeline: {e}")
            logger.info("Using simplified speaker detection")
            return {
                "battle_id": battle_id,
                "segments": [],
                "speakers": ["MC1", "MC2"],
                "note": "Simplified detection - pyannote not available",
            }

        # Apply diarization
        logger.info("Applying speaker diarization...")
        _update('PROCESSING', {'status': 'Processing audio...'})

        diarization = pipeline(audio_path)

        # Extract speaker segments
        segments = []
        speaker_set = set()

        for turn, _, speaker in diarization.itertracks(yields_label=True):
            segment = {
                "start_time": turn.start,
                "end_time": turn.end,
                "speaker": speaker,
                "duration": turn.end - turn.start,
            }
            segments.append(segment)
            speaker_set.add(speaker)

        logger.info(f"Found {len(segments)} segments from {len(speaker_set)} speakers")

        # Identify MC1 and MC2 (first two speakers)
        speakers = sorted(list(speaker_set))[:2]
        mc_mapping = {
            speakers[0]: "MC1",
            speakers[1]: "MC2" if len(speakers) > 1 else "MC1",
        }

        # Remap speakers
        for segment in segments:
            segment["speaker"] = mc_mapping.get(segment["speaker"], segment["speaker"])

        logger.info(f"Diarization completed for battle {battle_id}")

        return {
            "battle_id": battle_id,
            "segments": segments,
            "speakers": list(set(segment["speaker"] for segment in segments)),
            "total_segments": len(segments),
        }

    except Exception as e:
        logger.error(f"Diarization failed for battle {battle_id}: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()
