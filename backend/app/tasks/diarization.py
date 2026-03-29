"""
Diarization task - transcription with openai-whisper (large-v3)
+ speaker diarization with pyannote.audio (speaker-diarization-3.1).
"""

import logging
import os
import time
from pathlib import Path

import torch
from app.workers.celery_app import celery_app
from app.database import SessionLocal

logger = logging.getLogger(__name__)


def _extract_annotation(raw_output):
    """
    Extract a pyannote Annotation object from the pipeline output.
    Handles multiple pyannote.audio versions robustly.
    """
    # Direct Annotation object (has itertracks)
    if hasattr(raw_output, 'itertracks'):
        return raw_output

    # Wrapped in a dataclass/namedtuple (DiarizeOutput, etc.)
    for attr in ('speaker_diarization', 'annotation', 'diarization', 'output'):
        if hasattr(raw_output, attr):
            candidate = getattr(raw_output, attr)
            if hasattr(candidate, 'itertracks'):
                return candidate

    # Tuple (Annotation, embeddings)
    if isinstance(raw_output, (tuple, list)) and len(raw_output) > 0:
        if hasattr(raw_output[0], 'itertracks'):
            return raw_output[0]

    # Dict-like
    if hasattr(raw_output, 'keys'):
        for key in raw_output:
            val = raw_output[key]
            if hasattr(val, 'itertracks'):
                return val

    # Last resort: log everything for debugging
    attrs = [a for a in dir(raw_output) if not a.startswith('_')]
    raise RuntimeError(
        f"Cannot extract Annotation from {type(raw_output).__name__}. "
        f"Attributes: {attrs}"
    )


@celery_app.task(bind=True, name="tasks.diarize_speakers")
def diarize_speakers(self, battle_id: int, audio_path: str) -> dict:
    """
    Transcribe audio with openai-whisper large-v3 and identify speakers
    with pyannote speaker-diarization-3.1.

    Returns:
        Dictionary with full_text, speaker-labeled segments, and speakers list.
    """
    def _update(state, meta):
        if self.request.id:
            self.update_state(state=state, meta=meta)

    db = SessionLocal()
    try:
        logger.info(f"Starting transcription+diarization for battle {battle_id}")
        _update('PROCESSING', {'status': 'Preparing...'})

        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise RuntimeError("HF_TOKEN environment variable is not set.")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")

        # ── Step 1: Transcribe with openai-whisper large-v3 ──────────────
        import whisper

        _update('PROCESSING', {'status': 'Loading Whisper large-v3 model...'})
        t0 = time.time()
        whisper_model = whisper.load_model("medium", device=device)
        logger.info(f"Whisper large-v3 loaded in {time.time() - t0:.1f}s")

        _update('PROCESSING', {'status': 'Transcribing audio...'})
        t1 = time.time()
        whisper_result = whisper_model.transcribe(
            audio_path,
            language="es",
            task="transcribe",
            verbose=False,
        )
        logger.info(
            f"Transcription completed in {time.time() - t1:.1f}s: "
            f"{len(whisper_result.get('segments', []))} segments"
        )

        transcription_segments = []
        for seg in whisper_result.get("segments", []):
            transcription_segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            })

        full_text = whisper_result.get("text", "")

        # Free Whisper memory
        del whisper_model
        if device == "cuda":
            torch.cuda.empty_cache()

        # ── Step 2: Speaker diarization with pyannote ────────────────────
        from pyannote.audio import Pipeline as PyannotePipeline

        _update('PROCESSING', {'status': 'Loading diarization model...'})
        t2 = time.time()
        diarize_pipeline = PyannotePipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token,
        )
        diarize_pipeline = diarize_pipeline.to(torch.device(device))
        logger.info(f"Pyannote model loaded in {time.time() - t2:.1f}s")

        _update('PROCESSING', {'status': 'Identifying speakers (this may take several minutes)...'})
        t3 = time.time()
        raw_diarization = diarize_pipeline(audio_path)
        logger.info(f"Diarization completed in {time.time() - t3:.1f}s")

        annotation = _extract_annotation(raw_diarization)

        # Build speaker timeline
        speaker_timeline = []
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            speaker_timeline.append((turn.start, turn.end, speaker))

        logger.info(f"Diarization found {len(speaker_timeline)} speaker turns")

        del diarize_pipeline
        if device == "cuda":
            torch.cuda.empty_cache()

        # ── Step 3: Merge transcription + diarization ────────────────────
        segments = []
        speaker_set = set()

        for tseg in transcription_segments:
            best_speaker = _find_speaker(tseg["start"], tseg["end"], speaker_timeline)
            speaker_set.add(best_speaker)
            segments.append({
                "start_time": tseg["start"],
                "end_time": tseg["end"],
                "text": tseg["text"],
                "speaker": best_speaker,
                "duration": tseg["end"] - tseg["start"],
            })

        # ── Map SPEAKER_XX → MC1, MC2, ... ──────────────────────────────
        sorted_speakers = sorted(speaker_set)
        mc_mapping = {spk: f"MC{i + 1}" for i, spk in enumerate(sorted_speakers)}
        logger.info(f"Speaker mapping: {mc_mapping}")

        for seg in segments:
            seg["speaker"] = mc_mapping.get(seg["speaker"], seg["speaker"])

        mapped_speakers = [f"MC{i + 1}" for i in range(len(sorted_speakers))]

        logger.info(
            f"Done for battle {battle_id}: {len(segments)} segments, "
            f"{len(mapped_speakers)} speakers"
        )

        return {
            "battle_id": battle_id,
            "full_text": full_text,
            "segments": segments,
            "speakers": mapped_speakers,
            "total_segments": len(segments),
        }

    except Exception as e:
        logger.error(f"Diarization failed for battle {battle_id}: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()


def _find_speaker(start: float, end: float, speaker_timeline: list) -> str:
    """
    Find the speaker with the most overlap in the given time window.
    Falls back to 'SPEAKER_00' if no overlap is found.
    """
    best_speaker = "SPEAKER_00"
    best_overlap = 0.0

    for spk_start, spk_end, speaker in speaker_timeline:
        overlap_start = max(start, spk_start)
        overlap_end = min(end, spk_end)
        overlap = max(0.0, overlap_end - overlap_start)

        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = speaker

    return best_speaker
