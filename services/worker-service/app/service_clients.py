from __future__ import annotations

from typing import Any

import httpx

from .config import WorkerConfig, get_config


class ServiceClients:
    def __init__(self, config: WorkerConfig | None = None):
        self.config = config or get_config()

    def classify(self, ticket_id: str, customer_text: str) -> dict[str, Any]:
        return self._post(f"{self.config.classifier_service_url}/classify", {"ticket_id": ticket_id, "customer_text": customer_text})

    def score_urgency(self, ticket_id: str, customer_text: str, classification: dict[str, Any]) -> dict[str, Any]:
        return self._post(
            f"{self.config.urgency_service_url}/score-urgency",
            {"ticket_id": ticket_id, "customer_text": customer_text, "classification": classification},
        )

    def retrieve_evidence(self, ticket_id: str, customer_text: str, classification: dict[str, Any], urgency: dict[str, Any]) -> list[dict[str, Any]]:
        response = self._post(
            f"{self.config.rag_service_url}/rag/search",
            {
                "ticket_id": ticket_id,
                "customer_text": customer_text,
                "intent": classification["intent"],
                "urgency_level": urgency["urgency_level"],
                "top_k": 3,
            },
        )
        return response.get("results", [])

    def generate_draft(
        self,
        ticket_id: str,
        customer_text: str,
        classification: dict[str, Any],
        urgency: dict[str, Any],
        evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:
        response = self._post(
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
                "policy_context": evidence,
            },
        )
        return response.get("draft", response)

    def store_result(self, result: dict[str, Any]) -> dict[str, Any]:
        job_id = result.get("job_id") or result["ticket_id"]
        return self._post(
            f"{self.config.gateway_service_url}/internal/jobs/{job_id}/result",
            {"ticket_id": result["ticket_id"], "status": result["status"], "result": result},
            headers={"X-LocalBank-Worker-Token": self.config.worker_internal_token},
        )

    def _post(self, url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
        response = httpx.post(url, json=payload, headers=headers, timeout=self.config.timeout_seconds)
        response.raise_for_status()
        return response.json()
