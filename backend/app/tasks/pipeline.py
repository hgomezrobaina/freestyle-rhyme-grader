"""
Pipeline orchestration - coordinates the full processing pipeline.
"""

import logging
from celery import chain, group
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.battle import Battle, Verse, BattleStatus
from app.tasks.download import download_youtube_video, save_uploaded_file
from app.tasks.transcription import transcribe_audio
from app.tasks.voice_separation import separate_voices
from app.tasks.diarization import diarize_speakers
from app.services.battle_service import BattleService
from analysis.rhyme.metrics import RhymeMetricsCalculator

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.process_pipeline")
def process_pipeline(self, battle_id: int, source_type: str, source_path: str) -> dict:
    """
    Orchestrate the complete processing pipeline:
    1. Download/Save audio
    2. Transcribe with Whisper
    3. Separate voices with Demucs
    4. Diarize speakers with Pyannote
    5. Segment and analyze verses
    6. Calculate rhyme metrics

    Args:
        battle_id: ID of the battle
        source_type: "youtube", "upload"
        source_path: URL or file path

    Returns:
        Dictionary with final results
    """
    db = SessionLocal()
    try:
        logger.info(f"Pipeline started for battle {battle_id}")
        self.update_state(state='PROCESSING', meta={'current_step': 'Starting pipeline...'})

        # Step 1: Download or save file
        logger.info(f"Step 1: {source_type.upper()} download/save")
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 1/5: Preparing audio...'})

        if source_type == "youtube":
            download_result = download_youtube_video(battle_id, source_path)
            audio_path = download_result["audio_path"]
        elif source_type == "upload":
            # Assuming source_path is already saved, just get its path
            audio_path = source_path
        else:
            raise ValueError(f"Unknown source type: {source_type}")

        logger.info(f"Audio ready: {audio_path}")

        # Step 2: Transcribe
        logger.info("Step 2: Transcription")
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 2/5: Transcribing audio...'})

        transcription_result = transcribe_audio(battle_id, audio_path)
        full_text = transcription_result["full_text"]
        segments = transcription_result["segments"]

        logger.info(f"Transcription complete: {len(segments)} segments")

        # Step 3: Voice separation (optional, for now skip if it fails)
        logger.info("Step 3: Voice separation")
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 3/5: Separating voices...'})

        try:
            separation_result = separate_voices(battle_id, audio_path)
            logger.info("Voice separation successful")
        except Exception as e:
            logger.warning(f"Voice separation failed (non-critical): {e}")
            separation_result = {}

        # Step 4: Diarization
        logger.info("Step 4: Speaker diarization")
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 4/5: Identifying speakers...'})

        diarization_result = diarize_speakers(battle_id, audio_path)
        speaker_segments = diarization_result.get("segments", [])
        speakers = diarization_result.get("speakers", ["MC1", "MC2"])

        logger.info(f"Diarization complete: {speakers}")

        # Step 5: Segment verses and analyze
        logger.info("Step 5: Verse segmentation and analysis")
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 5/5: Analyzing verses...'})

        verses = segment_verses(
            battle_id,
            full_text,
            segments,
            speaker_segments
        )

        logger.info(f"Pipeline complete: {len(verses)} verses analyzed")

        # Update battle status
        battle = db.query(Battle).filter(Battle.id == battle_id).first()
        if battle:
            battle.status = BattleStatus.COMPLETED
            db.commit()

        result = {
            "battle_id": battle_id,
            "verses_count": len(verses),
            "speakers": speakers,
            "transcription_confidence": "medium", # From Whisper detect_language
            "status": "completed",
        }

        logger.info(f"Pipeline completed successfully for battle {battle_id}")
        return result

    except Exception as e:
        logger.error(f"Pipeline failed for battle {battle_id}: {str(e)}", exc_info=True)
        battle = db.query(Battle).filter(Battle.id == battle_id).first()
        if battle:
            battle.status = BattleStatus.FAILED
            db.commit()
        raise

    finally:
        db.close()


def segment_verses(
    battle_id: int,
    full_text: str,
    transcription_segments: list,
    speaker_segments: list
) -> list:
    """
    Segment transcribed text into individual verses based on speaker changes.

    Args:
        battle_id: ID of the battle
        full_text: Full transcription text
        transcription_segments: Time-aligned transcription segments
        speaker_segments: Speaker diarization segments

    Returns:
        List of verse dictionaries with timing and speaker info
    """
    db = SessionLocal()
    try:
        verses = []
        verse_number = 1
        current_speaker = None
        current_text = ""
        current_start = 0

        metrics_calculator = RhymeMetricsCalculator()

        # Simple approach: split by speaker changes
        for seg in speaker_segments:
            speaker = seg["speaker"]
            text = seg.get("text", "")

            # If speaker changed, save previous verse
            if speaker != current_speaker and current_text:
                # Create verse
                verse_data = {
                    "verse_number": verse_number,
                    "speaker": current_speaker or "MC1",
                    "text": current_text.strip(),
                    "start_time": current_start,
                    "end_time": seg["start_time"],
                }

                # Analyze rhymes
                metrics = metrics_calculator.calculate_metrics(verse_data["text"])

                # Save to database
                from app.models.battle import Verse, RhymeMetric

                verse = Verse(
                    battle_id=battle_id,
                    verse_number=verse_number,
                    speaker=current_speaker,
                    text=current_text.strip(),
                    duration_seconds=seg["start_time"] - current_start,
                )
                db.add(verse)
                db.flush()

                # Save metrics
                rhyme_metric = RhymeMetric(
                    verse_id=verse.id,
                    rhyme_density=metrics["rhyme_density"],
                    multisyllabic_ratio=metrics["multisyllabic_ratio"],
                    internal_rhymes_count=metrics["internal_rhymes_count"],
                    rhyme_diversity=metrics["rhyme_diversity"],
                    total_syllables=metrics["total_syllables"],
                    rhymed_syllables=metrics["rhymed_syllables"],
                    rhyme_types=metrics["rhyme_types"],
                )
                db.add(rhyme_metric)

                verses.append(verse_data)
                verse_number += 1
                current_text = ""

            current_speaker = speaker
            current_text += " " + text if current_text else text
            current_start = seg["start_time"]

        # Save last verse
        if current_text:
            metrics = metrics_calculator.calculate_metrics(current_text.strip())

            from app.models.battle import Verse, RhymeMetric

            verse = Verse(
                battle_id=battle_id,
                verse_number=verse_number,
                speaker=current_speaker,
                text=current_text.strip(),
            )
            db.add(verse)
            db.flush()

            rhyme_metric = RhymeMetric(
                verse_id=verse.id,
                rhyme_density=metrics["rhyme_density"],
                multisyllabic_ratio=metrics["multisyllabic_ratio"],
                internal_rhymes_count=metrics["internal_rhymes_count"],
                rhyme_diversity=metrics["rhyme_diversity"],
                total_syllables=metrics["total_syllables"],
                rhymed_syllables=metrics["rhymed_syllables"],
                rhyme_types=metrics["rhyme_types"],
            )
            db.add(rhyme_metric)

            verses.append({
                "verse_number": verse_number,
                "speaker": current_speaker,
                "text": current_text.strip(),
            })

        db.commit()
        logger.info(f"Segmented {len(verses)} verses for battle {battle_id}")
        return verses

    except Exception as e:
        logger.error(f"Verse segmentation failed: {str(e)}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()
