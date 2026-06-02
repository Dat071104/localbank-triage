from __future__ import annotations

from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import GatewayConfig, get_config
from .schemas import Employee


bearer_scheme = HTTPBearer(auto_error=False)


class DownstreamClients:
    def __init__(self, config: GatewayConfig):
        self.config = config

    def verify_token(self, token: str) -> Employee:
        data = self._get(f"{self.config.auth_service_url}/auth/me", headers={"Authorization": f"Bearer {token}"})
        employee = data["employee"]
        return Employee(
            employee_id=employee["employee_id"],
            role=employee["role"],
            display_name=employee.get("display_name"),
        )

    def classify(self, ticket_id: str, customer_text: str) -> dict[str, Any]:
        return self._post(
            f"{self.config.classifier_service_url}/classify",
            {"ticket_id": ticket_id, "customer_text": customer_text},
        )

    def score_urgency(self, ticket_id: str, customer_text: str, classification: dict[str, Any]) -> dict[str, Any]:
        return self._post(
            f"{self.config.urgency_service_url}/score-urgency",
            {"ticket_id": ticket_id, "customer_text": customer_text, "classification": classification},
        )

    def retrieve_evidence(self, ticket_id: str, customer_text: str, classification: dict[str, Any], urgency: dict[str, Any]) -> dict[str, Any]:
        return self._post(
            f"{self.config.rag_service_url}/rag/search",
            {
                "ticket_id": ticket_id,
                "customer_text": customer_text,
                "intent": classification["intent"],
                "urgency_level": urgency["urgency_level"],
                "top_k": 3,
            },
        )

    def generate_draft(
        self,
        ticket_id: str,
        customer_text: str,
        classification: dict[str, Any],
        urgency: dict[str, Any],
        policy_context: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._post(
            f"{self.config.llm_service_url}/draft/generate",
            {
                "ticket_id": ticket_id,
                "customer_text": customer_text,
                "classification": classification,
                "urgency": {
                    "urgency_score": urgency["urgency_score"],
                    "urgency_level": urgency["urgency_level"],
                    "reason_codes": urgency.get("reason_codes", []),
                    "requires_supervisor_approval": urgency["requires_supervisor_approval"],
                    "auto_send_allowed": urgency["auto_send_allowed"],
                },
                "policy_context": policy_context,
            },
        )

    def _get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        try:
            response = httpx.get(url, headers=headers, timeout=self.config.timeout_seconds)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"code": "DOWNSTREAM_GET_FAILED", "message": "A downstream service is unavailable.", "stage": "downstream"},
            ) from exc

    def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.post(url, json=payload, timeout=self.config.timeout_seconds)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            stage = "downstream"
            if "classifier" in url:
                stage = "classifier"
            elif "urgency" in url:
                stage = "urgency"
            elif "rag" in url:
                stage = "rag"
            elif "llm" in url:
                stage = "llm"
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"code": "DOWNSTREAM_POST_FAILED", "message": "A downstream service is unavailable.", "stage": stage},
            ) from exc


def get_clients() -> DownstreamClients:
    return DownstreamClients(get_config())


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    clients: DownstreamClients = Depends(get_clients),
) -> Employee:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return clients.verify_token(credentials.credentials)
