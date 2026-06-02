from __future__ import annotations

from app.celery_app import create_celery_app
from app.tasks import triage_ticket


def test_celery_app_config_loads() -> None:
    app = create_celery_app()
    assert app.conf.task_always_eager is True
    assert str(app.conf.broker_url).startswith("redis://")


def test_worker_task_can_run_in_eager_mode(monkeypatch) -> None:
    def fake_pipeline(job):
        class Result:
            def model_dump(self):
                return {"ticket_id": job.ticket_id, "status": "DRAFT_READY", "errors": []}

        return Result()

    monkeypatch.setattr("app.tasks.run_triage_pipeline", fake_pipeline)
    result = triage_ticket.apply(args=[{"ticket_id": "TASK-1", "customer_text": "Xin hỏi thông tin."}])
    assert result.get()["status"] == "DRAFT_READY"

