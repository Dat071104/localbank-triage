from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Employee:
    employee_id: str
    full_name: str
    display_name: str
    role: str
    department: str
    branch_code: str
    access_code_hash: str
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class Session:
    session_token_hash: str
    employee_id: str
    device_id: str
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
