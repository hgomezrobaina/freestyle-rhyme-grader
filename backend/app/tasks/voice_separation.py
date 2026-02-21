"""
Voice separation task - handles audio source separation using Demucs.
"""

import logging
from pathlib import Path
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torch
import torchaudio
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.battle import Battle

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.separate_voices")
def separate_voices(self, battle_id: int, audio_path: str) -> dict:
    """
    Separate voices from background music/noise using Demucs.

    Args:
        battle_id: ID of the battle
        audio_path: Path to audio file

    Returns:
        Dictionary with paths to separated sources
    """
    def _update(state, meta):
        if self.request.id:
            self.update_state(state=state, meta=meta)

    db = SessionLocal()
    try:
        logger.info(f"Starting voice separation for battle {battle_id}")
        _update('PROCESSING', {'status': 'Separating voices from background...'})

        # Verify file exists
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load audio
        logger.info(f"Loading audio: {audio_path}")
        waveform, sample_rate = torchaudio.load(audio_path)

        # Move to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        waveform = waveform.to(device)

        # Load Demucs model
        logger.info("Loading Demucs model...")
        _update('PROCESSING', {'status': 'Loading Demucs model...'})
        model = get_model("htdemucs").to(device)

        # Apply separation
        logger.info("Applying voice separation...")
        _update('PROCESSING', {'status': 'Separating sources...'})

        # Ensure correct number of channels
        if waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)
        if waveform.size(0) > 2:
            waveform = waveform[:2]
        elif waveform.size(0) == 1:
            waveform = waveform.repeat(2, 1)

        with torch.no_grad():
            sources = apply_model(model, waveform[None], device=device, split=True, overlap=0.1)[0]

        logger.info(f"Separation completed, got {sources.size(0)} sources")

        # Save separated sources
        output_dir = Path(audio_path).parent / "separated"
        output_dir.mkdir(parents=True, exist_ok=True)

        source_names = ["drums", "bass", "other", "vocals"]  # Demucs source order
        saved_paths = {}

        for i, name in enumerate(source_names):
            if i < sources.size(0):
                output_path = output_dir / f"{name}.wav"
                source = sources[i].cpu()
                torchaudio.save(output_path, source, sample_rate)
                saved_paths[name] = str(output_path)
                logger.info(f"Saved {name}: {output_path}")

        logger.info(f"Voice separation completed for battle {battle_id}")

        return {
            "battle_id": battle_id,
            "separated_sources": saved_paths,
            "sample_rate": sample_rate,
        }

    except Exception as e:
        logger.error(f"Voice separation failed for battle {battle_id}: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()
