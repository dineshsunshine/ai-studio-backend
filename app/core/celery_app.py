"""
Celery configuration for asynchronous video generation tasks
"""

from celery import Celery
from app.core.config import settings
import os

# Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "ai_studio",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.video_worker"]  # Import worker tasks
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes max per task
    task_soft_time_limit=1500,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
)

# Task routing (optional, for future scaling)
celery_app.conf.task_routes = {
    "app.workers.video_worker.process_video_generation": {"queue": "video_generation"},
}

