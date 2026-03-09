"""
Diarization task - handles speaker identification and segmentation using Pyannote.
"""

import logging
import os
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

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise RuntimeError("HF_TOKEN environment variable is not set. Required for pyannote diarization.")

        import time
        t0 = time.time()
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.0",
            token=hf_token
        )
        logger.info(f"Pyannote model loaded in {time.time() - t0:.1f}s")

        pipeline = pipeline.to(device)

        # Apply diarization
        logger.info("Applying speaker diarization (this may take a while on CPU)...")
        _update('PROCESSING', {'status': 'Processing audio (this may take several minutes)...'})

        t1 = time.time()
        diarization = pipeline(audio_path)
        logger.info(f"Diarization completed in {time.time() - t1:.1f}s")

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

        # Map all detected speakers to MC labels (MC1, MC2, MC3, ...)
        speakers = sorted(list(speaker_set))
        mc_mapping = {
            speaker: f"MC{i + 1}"
            for i, speaker in enumerate(speakers)
        }

        logger.info(f"Speaker mapping: {mc_mapping}")

        # Remap speakers
        for segment in segments:
            segment["speaker"] = mc_mapping.get(
                segment["speaker"],
                segment["speaker"]
            )

        mapped_speakers = [f"MC{i + 1}" for i in range(len(speakers))]
        logger.info(f"Diarization completed for battle {battle_id}: {len(mapped_speakers)} speakers detected")

        return {
            "battle_id": battle_id,
            "segments": segments,
            "speakers": mapped_speakers,
            "total_segments": len(segments),
        }

    except Exception as e:
        logger.error(f"Diarization failed for battle {battle_id}: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()
