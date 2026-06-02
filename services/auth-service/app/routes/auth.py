from __future__ import annotations

import os
from datetime import UTC, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import db
from ..schemas import AuthMeResponse, EmployeeView, LoginRequest, LoginResponse, LogoutResponse
from ..security import generate_session_token, verify_access_code

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)
INVALID_CREDENTIALS = "Invalid employee credentials"


def session_expire_minutes() -> int:
    return int(os.getenv("AUTH_SESSION_EXPIRE_MINUTES", "60"))


def active_employee_from_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> tuple[db.Employee, str]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    session = db.get_session(credentials.credentials)
    if session is None or session.revoked_at is not None or session.expires_at <= db.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    employee = db.get_employee(session.employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return employee, credentials.credentials


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    employee = db.get_employee(payload.employee_id)
    valid_employee = (
        employee is not None
        and employee.full_name == payload.full_name
        and verify_access_code(payload.access_code, employee.access_code_hash)
    )

    if not valid_employee or employee is None:
        db.record_login_attempt(
            employee_id=payload.employee_id,
            full_name=payload.full_name,
            device_id=payload.device_id,
            success=False,
            failure_reason="invalid_credentials",
        )
        db.add_audit_log(
            action="login",
            status="failure",
            employee_id=payload.employee_id,
            device_id=payload.device_id,
            details={"reason": "invalid_credentials"},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)

    token = generate_session_token()
    expires_at = db.utcnow() + timedelta(minutes=session_expire_minutes())
    db.create_session(
        employee_id=employee.employee_id,
        device_id=payload.device_id,
        raw_token=token,
        expires_at=expires_at,
    )
    db.record_login_attempt(
        employee_id=payload.employee_id,
        full_name=payload.full_name,
        device_id=payload.device_id,
        success=True,
    )
    db.add_audit_log(
        action="login",
        status="success",
        employee_id=employee.employee_id,
        device_id=payload.device_id,
        details={"role": employee.role},
    )
    return LoginResponse(
        access_token=token,
        expires_in=session_expire_minutes() * 60,
        employee=EmployeeView.model_validate(db.serialize_employee(employee)),
    )


@router.get("/me", response_model=AuthMeResponse)
def me(active: tuple[db.Employee, str] = Depends(active_employee_from_token)) -> AuthMeResponse:
    employee, _ = active
    return AuthMeResponse(employee=EmployeeView.model_validate(db.serialize_employee(employee)))


@router.post("/logout", response_model=LogoutResponse)
def logout(active: tuple[db.Employee, str] = Depends(active_employee_from_token)) -> LogoutResponse:
    employee, raw_token = active
    db.revoke_session(raw_token)
    db.add_audit_log(
        action="logout",
        status="success",
        employee_id=employee.employee_id,
        device_id=None,
    )
    return LogoutResponse(detail="Session revoked")
