"""
Celery app configuration and initialization.
"""

from celery import Celery
from app.config import get_settings
import logging

settings = get_settings()

# Create Celery app
celery_app = Celery(
    'freestyle_callificator',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks from all app packages
celery_app.autodiscover_tasks(['app.tasks'])

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery connectivity."""
    logger.info(f'Request: {self.request!r}')

if __name__ == '__main__':
    celery_app.start()
