from celery import Celery
from app.config import settings

celery = Celery(
    "rag_kb_assistant",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.update(
    task_track_started=True,
    task_time_limit=120,
    task_soft_time_limit=90,
    worker_prefetch_multiplier=1,
)
