from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterator

from .models import Employee, Session
from .security import hash_access_code, hash_session_token

SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) > 3 else SERVICE_ROOT
DEFAULT_DATABASE_URL = "sqlite:///data/auth/auth.db"


def utcnow() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def get_database_url() -> str:
    return os.getenv("AUTH_DATABASE_URL", DEFAULT_DATABASE_URL)


def database_path_from_url(database_url: str | None = None) -> Path:
    url = database_url or get_database_url()
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        raise ValueError("AUTH_DATABASE_URL must use sqlite:///")

    raw_path = url[len(prefix) :]
    path = Path(raw_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


@contextmanager
def get_connection(database_url: str | None = None) -> Iterator[sqlite3.Connection]:
    db_path = database_path_from_url(database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db(database_url: str | None = None) -> None:
    with get_connection(database_url) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS employees (
                employee_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT NOT NULL,
                branch_code TEXT NOT NULL,
                access_code_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS local_sessions (
                session_token_hash TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(employee_id) REFERENCES employees(employee_id)
            );

            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                full_name TEXT NOT NULL,
                device_id TEXT NOT NULL,
                success INTEGER NOT NULL,
                failure_reason TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS auth_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                device_id TEXT,
                created_at TEXT NOT NULL,
                details TEXT
            );
            """
        )


def load_seed_employees(seed_path: Path) -> list[dict[str, str]]:
    return json.loads(seed_path.read_text(encoding="utf-8"))


def employee_count(database_url: str | None = None) -> int:
    with get_connection(database_url) as connection:
        row = connection.execute("SELECT COUNT(*) AS count FROM employees").fetchone()
    return int(row["count"])


def seed_employees(seed_records: list[dict[str, str]], database_url: str | None = None) -> int:
    init_db(database_url)
    seeded_at = utcnow().isoformat()
    prepared_rows = [
        {
            "employee_id": record["employee_id"],
            "full_name": record["full_name"],
            "display_name": record["display_name"],
            "role": record["role"],
            "department": record["department"],
            "branch_code": record["branch_code"],
            "access_code_hash": hash_access_code(record["access_code"]),
            "created_at": seeded_at,
            "updated_at": seeded_at,
        }
        for record in seed_records
    ]

    with get_connection(database_url) as connection:
        connection.executemany(
            """
            INSERT INTO employees (
                employee_id,
                full_name,
                display_name,
                role,
                department,
                branch_code,
                access_code_hash,
                created_at,
                updated_at
            ) VALUES (
                :employee_id,
                :full_name,
                :display_name,
                :role,
                :department,
                :branch_code,
                :access_code_hash,
                :created_at,
                :updated_at
            )
            ON CONFLICT(employee_id) DO UPDATE SET
                full_name = excluded.full_name,
                display_name = excluded.display_name,
                role = excluded.role,
                department = excluded.department,
                branch_code = excluded.branch_code,
                access_code_hash = excluded.access_code_hash,
                updated_at = excluded.updated_at
            """,
            prepared_rows,
        )
    return len(prepared_rows)


def get_employee(employee_id: str, database_url: str | None = None) -> Employee | None:
    with get_connection(database_url) as connection:
        row = connection.execute(
            """
            SELECT employee_id, full_name, display_name, role, department,
                   branch_code, access_code_hash, created_at, updated_at
            FROM employees
            WHERE employee_id = ?
            """,
            (employee_id,),
        ).fetchone()

    if row is None:
        return None

    return Employee(
        employee_id=row["employee_id"],
        full_name=row["full_name"],
        display_name=row["display_name"],
        role=row["role"],
        department=row["department"],
        branch_code=row["branch_code"],
        access_code_hash=row["access_code_hash"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def record_login_attempt(
    employee_id: str,
    full_name: str,
    device_id: str,
    success: bool,
    failure_reason: str | None = None,
    database_url: str | None = None,
) -> None:
    with get_connection(database_url) as connection:
        connection.execute(
            """
            INSERT INTO login_attempts (
                employee_id,
                full_name,
                device_id,
                success,
                failure_reason,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                full_name,
                device_id,
                int(success),
                failure_reason,
                utcnow().isoformat(),
            ),
        )


def add_audit_log(
    action: str,
    status: str,
    employee_id: str | None,
    device_id: str | None,
    details: dict[str, str] | None = None,
    database_url: str | None = None,
) -> None:
    with get_connection(database_url) as connection:
        connection.execute(
            """
            INSERT INTO auth_audit_logs (
                employee_id,
                action,
                status,
                device_id,
                created_at,
                details
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                action,
                status,
                device_id,
                utcnow().isoformat(),
                json.dumps(details or {}, ensure_ascii=False),
            ),
        )


def create_session(
    employee_id: str,
    device_id: str,
    raw_token: str,
    expires_at: datetime,
    database_url: str | None = None,
) -> None:
    with get_connection(database_url) as connection:
        connection.execute(
            """
            INSERT INTO local_sessions (
                session_token_hash,
                employee_id,
                device_id,
                expires_at,
                revoked_at,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                hash_session_token(raw_token),
                employee_id,
                device_id,
                expires_at.isoformat(),
                None,
                utcnow().isoformat(),
            ),
        )


def get_session(raw_token: str, database_url: str | None = None) -> Session | None:
    with get_connection(database_url) as connection:
        row = connection.execute(
            """
            SELECT session_token_hash, employee_id, device_id,
                   expires_at, revoked_at, created_at
            FROM local_sessions
            WHERE session_token_hash = ?
            """,
            (hash_session_token(raw_token),),
        ).fetchone()

    if row is None:
        return None

    revoked_at = row["revoked_at"]
    return Session(
        session_token_hash=row["session_token_hash"],
        employee_id=row["employee_id"],
        device_id=row["device_id"],
        expires_at=datetime.fromisoformat(row["expires_at"]),
        revoked_at=datetime.fromisoformat(revoked_at) if revoked_at else None,
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def revoke_session(raw_token: str, database_url: str | None = None) -> bool:
    with get_connection(database_url) as connection:
        existing = connection.execute(
            """
            SELECT revoked_at
            FROM local_sessions
            WHERE session_token_hash = ?
            """,
            (hash_session_token(raw_token),),
        ).fetchone()
        if existing is None:
            return False
        if existing["revoked_at"] is not None:
            return True
        connection.execute(
            """
            UPDATE local_sessions
            SET revoked_at = ?
            WHERE session_token_hash = ?
            """,
            (utcnow().isoformat(), hash_session_token(raw_token)),
        )
        return True


def serialize_employee(employee: Employee) -> dict[str, str]:
    payload = asdict(employee)
    payload.pop("access_code_hash", None)
    payload.pop("full_name", None)
    payload.pop("created_at", None)
    payload.pop("updated_at", None)
    return payload
