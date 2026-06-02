from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EmployeeView(BaseModel):
    employee_id: str
    display_name: str
    role: str
    department: str
    branch_code: str


class LoginRequest(BaseModel):
    employee_id: str = Field(min_length=1, max_length=64)
    full_name: str = Field(min_length=1, max_length=128)
    access_code: str = Field(min_length=1, max_length=128)
    device_id: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    employee: EmployeeView


class HealthResponse(BaseModel):
    status: str


class AuthMeResponse(BaseModel):
    employee: EmployeeView
    model_config = ConfigDict(extra="forbid")


class LogoutResponse(BaseModel):
    detail: str
