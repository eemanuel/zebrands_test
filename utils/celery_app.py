# coding=utf-8

from django.conf import settings

from celery import Celery

# Initial Celery app configuration

celery_app = Celery("Celery Zebrands")
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    task_ignore_result=settings.CELERY_IGNORE_RESULT,
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
)
celery_app.autodiscover_tasks()
