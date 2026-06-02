from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture()
def seeded_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, Path]:
    db_path = tmp_path / "auth-test.db"
    monkeypatch.setenv("AUTH_DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("AUTH_SESSION_EXPIRE_MINUTES", "60")
    db.init_db()
    seed_path = Path(__file__).resolve().parents[1] / "employees_seed.json"
    seed_records = json.loads(seed_path.read_text(encoding="utf-8"))
    db.seed_employees(seed_records)
    client = TestClient(app)
    return client, db_path


def login_payload(**overrides: str) -> dict[str, str]:
    payload = {
        "employee_id": "LBT-CS-0001",
        "full_name": "Nguyễn Hà Trâm",
        "access_code": "Tram@112233",
        "device_id": "LOCAL-DESKTOP-01",
    }
    payload.update(overrides)
    return payload


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health_returns_ok(seeded_client: tuple[TestClient, Path]) -> None:
    client, _ = seeded_client
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_seed_script_creates_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "seeded.db"
    monkeypatch.setenv("AUTH_DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    seed_path = Path(__file__).resolve().parents[1] / "employees_seed.json"
    seeded = db.seed_employees(json.loads(seed_path.read_text(encoding="utf-8")))
    assert seeded == 4
    assert db_path.exists()
    with sqlite3.connect(db_path) as connection:
        count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    assert count == 4


def test_valid_login_works(seeded_client: tuple[TestClient, Path]) -> None:
    client, _ = seeded_client
    response = client.post("/auth/login", json=login_payload())
    body = response.json()
    assert response.status_code == 200
    assert body["token_type"] == "bearer"
    assert body["access_token"] != "LBT-CS-0001"
    assert body["employee"]["role"] == "CS_AGENT"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("access_code", "Wrong@112233"),
        ("full_name", "Nguyen Ha Tram"),
        ("employee_id", "LBT-CS-9999"),
    ],
)
def test_invalid_credentials_share_same_failure_message(
    seeded_client: tuple[TestClient, Path],
    field: str,
    value: str,
) -> None:
    client, _ = seeded_client
    response = client.post("/auth/login", json=login_payload(**{field: value}))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid employee credentials"}


def test_auth_me_works_with_valid_token(seeded_client: tuple[TestClient, Path]) -> None:
    client, _ = seeded_client
    login = client.post("/auth/login", json=login_payload()).json()
    response = client.get("/auth/me", headers=auth_headers(login["access_token"]))
    assert response.status_code == 200
    body = response.json()
    assert body["employee"]["employee_id"] == "LBT-CS-0001"
    assert "access_code_hash" not in response.text


def test_auth_me_fails_with_invalid_token(seeded_client: tuple[TestClient, Path]) -> None:
    client, _ = seeded_client
    response = client.get("/auth/me", headers=auth_headers("invalid-token"))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_logout_revokes_session_and_blocks_me(seeded_client: tuple[TestClient, Path]) -> None:
    client, _ = seeded_client
    login = client.post("/auth/login", json=login_payload()).json()
    token = login["access_token"]
    response = client.post("/auth/logout", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json() == {"detail": "Session revoked"}

    me_response = client.get("/auth/me", headers=auth_headers(token))
    assert me_response.status_code == 401
    assert me_response.json() == {"detail": "Invalid or expired token"}


def test_logout_handles_already_revoked_token_as_invalid_session(
    seeded_client: tuple[TestClient, Path],
) -> None:
    client, _ = seeded_client
    login = client.post("/auth/login", json=login_payload()).json()
    token = login["access_token"]
    client.post("/auth/logout", headers=auth_headers(token))
    response = client.post("/auth/logout", headers=auth_headers(token))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}


def test_db_does_not_store_plaintext_and_attempts_are_recorded(
    seeded_client: tuple[TestClient, Path],
) -> None:
    client, db_path = seeded_client
    client.post("/auth/login", json=login_payload())
    client.post("/auth/login", json=login_payload(access_code="Wrong@112233"))

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT access_code_hash FROM employees WHERE employee_id = ?",
            ("LBT-CS-0001",),
        ).fetchall()
        assert rows[0][0] != "Tram@112233"
        attempts = connection.execute(
            "SELECT success, failure_reason FROM login_attempts ORDER BY id"
        ).fetchall()

    assert attempts == [(1, None), (0, "invalid_credentials")]


def test_tests_use_temporary_db_not_repo_db(seeded_client: tuple[TestClient, Path]) -> None:
    _, db_path = seeded_client
    repo_db = Path(__file__).resolve().parents[3] / "data" / "auth" / "auth.db"
    assert db_path != repo_db
