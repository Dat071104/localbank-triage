from __future__ import annotations

from fastapi import HTTPException, status

from .schemas import Employee


READ_ROLES = {"CS_AGENT", "SUPERVISOR", "AUDITOR", "ADMIN"}
WRITE_ROLES = {"CS_AGENT", "SUPERVISOR", "ADMIN"}


def require_role(user: Employee, allowed: set[str]) -> None:
    if user.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role is not allowed for this action")


def can_approve(role: str, risk_level: str) -> bool:
    if role == "ADMIN":
        return True
    if role == "SUPERVISOR":
        return risk_level in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    if role == "CS_AGENT":
        return risk_level in {"LOW", "MEDIUM"}
    return False


def assert_can_approve(user: Employee, risk_level: str) -> None:
    if not can_approve(user.role, risk_level):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role cannot approve this ticket risk level")

