"""Celery tasks package"""
from app.tasks import download, transcription, voice_separation, diarization, pipeline, semantic_evaluation
