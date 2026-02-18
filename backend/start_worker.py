#!/usr/bin/env python
"""
Celery worker starter script.

Run this in a separate terminal to start the Celery worker:
    python start_worker.py
"""

import os
import sys
from app.workers.celery_app import celery_app

if __name__ == '__main__':
    argv = [
        'worker',
        '--loglevel=info',
        '--concurrency=2',  # 2 concurrent tasks
        '--max-tasks-per-child=100',
    ]

    print("Starting Celery Worker...")
    print("Make sure Redis is running: docker-compose up -d")
    print("")

    celery_app.worker_main(argv)
