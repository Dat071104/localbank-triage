from __future__ import annotations

from celery import Celery

from .config import get_config


def create_celery_app() -> Celery:
    config = get_config()
    app = Celery("localbank_worker", broker=config.broker_url, backend=config.result_backend)
    app.conf.update(
        task_always_eager=config.task_always_eager,
        task_eager_propagates=True,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
    )
    return app


celery_app = create_celery_app()

