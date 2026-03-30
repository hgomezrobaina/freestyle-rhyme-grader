"""
Pipeline orchestration - coordinates the full processing pipeline.
"""

import logging
import time
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.battle import Battle, BattleStatus, BattleFormat, PipelineStep
from app.models.mc_context import BattleParticipant
from app.tasks.download import download_youtube_video
from app.tasks.voice_separation import separate_voices
from app.tasks.diarization import diarize_speakers

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.process_pipeline")
def process_pipeline(self, battle_id: int, source_type: str, source_path: str) -> dict:
    """
    Upload pipeline: download, separate voices, and identify MCs.
    Analysis (verse segmentation + rhyme metrics) is triggered separately.

    Args:
        battle_id: ID of the battle
        source_type: "youtube", "upload"
        source_path: URL or file path

    Returns:
        Dictionary with diarization results
    """
    db = SessionLocal()

    def _set_step(step: PipelineStep):
        """Persist the current pipeline step to the database."""
        db.query(Battle).filter(Battle.id == battle_id).update(
            {Battle.progress_step: step}
        )
        db.commit()

    try:
        logger.info(f"Pipeline started for battle {battle_id}")
        self.update_state(state='PROCESSING', meta={'current_step': 'Starting pipeline...'})

        # Step 1: Download or save file
        logger.info(f"Step 1: {source_type.upper()} download/save")
        _set_step(PipelineStep.DOWNLOAD)
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

        # Step 2: Voice separation (optional)
        logger.info("Step 2: Voice separation")
        _set_step(PipelineStep.SEPARATE)
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 2/4: Separating voices...'})

        try:
            separate_voices(battle_id, audio_path)
            logger.info("Voice separation successful")
        except Exception as e:
            logger.warning(f"Voice separation failed (non-critical): {e}")

        # Step 3: Transcription + Diarization (combined via WhisperX)
        logger.info("Step 3: Transcription + Speaker diarization")
        _set_step(PipelineStep.DIARIZE)
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 3/4: Transcribing and identifying speakers...'})

        diarization_result = diarize_speakers(battle_id, audio_path)
        segments = diarization_result.get("segments", [])
        speakers = diarization_result.get("speakers", ["MC1", "MC2"])

        logger.info(f"Diarization complete: {speakers}")

        # Step 4.5: Create BattleParticipant records from detected speakers
        existing_participants = db.query(BattleParticipant).filter(
            BattleParticipant.battle_id == battle_id
        ).all()

        speaker_to_participant = {}
        if not existing_participants:
            # Assign teams alternating: speaker 0→team0, 1→team1, 2→team0, 3→team1...
            team_counters = {}  # track position_in_team per team
            for i, speaker_label in enumerate(speakers):
                team = i % 2
                pos = team_counters.get(team, 0)
                team_counters[team] = pos + 1
                participant = BattleParticipant(
                    battle_id=battle_id,
                    mc_name=f"MC {i + 1}",
                    team_number=team,
                    position_in_team=pos,
                )
                db.add(participant)
                db.flush()
                speaker_to_participant[speaker_label] = participant.id

            db.commit()
            
            logger.info(f"Created {len(speakers)} auto-detected participants for battle {battle_id}")
        else:
            # Map existing participants to speaker labels by team order
            sorted_participants = sorted(existing_participants, key=lambda p: (p.team_number, p.position_in_team))
            for i, speaker_label in enumerate(speakers):
                if i < len(sorted_participants):
                    speaker_to_participant[speaker_label] = sorted_participants[i].id
            
            logger.info(f"Mapped {len(speaker_to_participant)} existing participants to speakers")

        # Auto-detect battle_format if not set
        battle = db.query(Battle).filter(Battle.id == battle_id).first()
        if battle and not battle.battle_format:
            num_speakers = len(speakers)
            format_map = {
                2: BattleFormat.ONE_VS_ONE,
                4: BattleFormat.TWO_VS_TWO,
                6: BattleFormat.THREE_VS_THREE,
            }
            battle.battle_format = format_map.get(num_speakers, BattleFormat.ONE_VS_ONE)
            db.commit()

        # Step 4: Segment verses (without rhyme metrics)
        logger.info("Step 4: Verse segmentation")
        _set_step(PipelineStep.ANALYZE)
        self.update_state(state='PROCESSING', meta={'current_step': 'Step 4/4: Segmenting verses...'})

        full_text = diarization_result.get("full_text", "")
        verses = segment_verses(
            battle_id, full_text, segments, segments, speaker_to_participant,
        )

        logger.info(f"Pipeline complete: {len(verses)} verses segmented")

        # Mark as DIARIZED — rhyme analysis is triggered separately
        battle = db.query(Battle).filter(Battle.id == battle_id).first()
        if battle:
            battle.status = BattleStatus.DIARIZED
            battle.progress_step = None
            db.commit()

        result = {
            "battle_id": battle_id,
            "speakers": speakers,
            "verses_count": len(verses),
            "status": "diarized",
        }

        logger.info(f"Upload pipeline completed for battle {battle_id}")

        return result

    except Exception as e:
        logger.error(f"Pipeline failed for battle {battle_id}: {str(e)}", exc_info=True)
        # Use a fresh session to guarantee the status update commits
        # (the main session may be in a broken state after the error)
        fail_db = SessionLocal()
        try:
            battle = fail_db.query(Battle).filter(Battle.id == battle_id).first()
            if battle:
                battle.status = BattleStatus.FAILED
                fail_db.commit()
                logger.info(f"Battle {battle_id} marked as FAILED")
        except Exception as db_err:
            logger.error(f"Could not mark battle {battle_id} as FAILED: {db_err}")
            fail_db.rollback()
        finally:
            fail_db.close()
        raise

    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.analyze_battle")
def analyze_battle(self, battle_id: int) -> dict:
    """
    Calculate rhyme metrics for existing verses of a diarized battle.
    """
    from app.models.battle import Verse, RhymeMetric
    from analysis.rhyme.metrics import RhymeMetricsCalculator

    db = SessionLocal()
    try:
        battle = db.query(Battle).filter(Battle.id == battle_id).first()
        if not battle:
            raise ValueError(f"Battle {battle_id} not found")

        if battle.status not in (BattleStatus.DIARIZED, BattleStatus.FAILED):
            raise ValueError(f"Battle {battle_id} is not ready for analysis (status={battle.status})")

        battle.status = BattleStatus.PROCESSING
        battle.progress_step = PipelineStep.ANALYZE
        db.commit()

        verses = db.query(Verse).filter(Verse.battle_id == battle_id).order_by(Verse.verse_number).all()
        if not verses:
            raise ValueError(f"Battle {battle_id} has no verses to analyze")

        metrics_calculator = RhymeMetricsCalculator()
        logger.info(f"Analyzing {len(verses)} verses for battle {battle_id}")
        self.update_state(state='PROCESSING', meta={'current_step': 'Analyzing rhymes...'})

        for i, verse in enumerate(verses):
            # Skip if already has metrics
            if verse.rhyme_metric:
                continue

            logger.info(f"[Analyze] Verse {i+1}/{len(verses)} (id={verse.id})")
            metrics = metrics_calculator.calculate_metrics(verse.text)

            rhyme_metric = RhymeMetric(
                verse_id=verse.id,
                rhyme_density=metrics.rhyme_density,
                multisyllabic_ratio=metrics.multisyllabic_ratio,
                internal_rhymes_count=metrics.internal_rhymes_count,
                rhyme_diversity=metrics.rhyme_diversity,
                total_syllables=metrics.total_syllables,
                rhymed_syllables=metrics.rhymed_syllables,
                rhyme_types=metrics.rhyme_types,
            )
            db.add(rhyme_metric)

        db.commit()

        battle.status = BattleStatus.COMPLETED
        battle.progress_step = None
        db.commit()

        logger.info(f"Analysis complete for battle {battle_id}: {len(verses)} verses")
        return {
            "battle_id": battle_id,
            "verses_count": len(verses),
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"Analysis failed for battle {battle_id}: {str(e)}", exc_info=True)
        fail_db = SessionLocal()
        try:
            b = fail_db.query(Battle).filter(Battle.id == battle_id).first()
            if b:
                b.status = BattleStatus.FAILED
                b.progress_step = PipelineStep.ANALYZE
                fail_db.commit()
        except Exception as db_err:
            logger.error(f"Could not mark battle {battle_id} as FAILED: {db_err}")
            fail_db.rollback()
        finally:
            fail_db.close()
        raise

    finally:
        db.close()


def segment_verses(
    battle_id: int,
    full_text: str,
    transcription_segments: list,
    speaker_segments: list,
    speaker_to_participant: dict = None,
) -> list:
    """
    Segment transcribed text into individual verses based on speaker changes.
    Only creates Verse records — rhyme metrics are calculated separately.
    """
    from app.models.battle import Verse

    db = SessionLocal()
    try:
        verses = []
        verse_number = 1
        current_speaker = None
        current_text = ""
        current_start = 0

        t_start = time.time()
        total_segments = len(speaker_segments)
        logger.info(f"[SegmentVerses] Starting: {total_segments} speaker segments")

        for seg_idx, seg in enumerate(speaker_segments):
            if (seg_idx + 1) % 20 == 0:
                logger.info(f"[SegmentVerses] Segment {seg_idx+1}/{total_segments}")

            speaker = seg["speaker"]
            text = seg.get("text", "")

            if speaker != current_speaker and current_text:
                verse = Verse(
                    battle_id=battle_id,
                    verse_number=verse_number,
                    speaker=current_speaker,
                    participant_id=speaker_to_participant.get(current_speaker) if speaker_to_participant else None,
                    text=current_text.strip(),
                    duration_seconds=seg["start_time"] - current_start,
                )
                db.add(verse)

                verses.append({
                    "verse_number": verse_number,
                    "speaker": current_speaker or "MC1",
                    "text": current_text.strip(),
                    "start_time": current_start,
                    "end_time": seg["start_time"],
                })
                verse_number += 1
                current_text = ""

            current_speaker = speaker
            current_text += " " + text if current_text else text
            current_start = seg["start_time"]

        # Save last verse
        if current_text:
            verse = Verse(
                battle_id=battle_id,
                verse_number=verse_number,
                speaker=current_speaker,
                participant_id=speaker_to_participant.get(current_speaker) if speaker_to_participant else None,
                text=current_text.strip(),
            )
            db.add(verse)

            verses.append({
                "verse_number": verse_number,
                "speaker": current_speaker,
                "text": current_text.strip(),
            })

        db.commit()
        logger.info(f"[SegmentVerses] Segmented {len(verses)} verses in {time.time() - t_start:.1f}s")

        return verses

    except Exception as e:
        logger.error(f"Verse segmentation failed: {str(e)}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()
