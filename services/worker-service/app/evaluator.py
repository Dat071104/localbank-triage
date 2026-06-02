from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .pipeline import run_triage_pipeline
from .schemas import PipelineResult, TriageJobRequest


THRESHOLDS = {
    "urgency_safety_rate": 0.95,
    "draft_json_valid_rate": 1.0,
    "draft_safety_rate": 1.0,
    "supervisor_rule_pass_rate": 1.0,
    "hallucination_free_rate": 0.95,
    "pipeline_success_rate": 0.90,
    "overall_product_quality_rate": 0.90,
}


class RuleBasedEvaluationClients:
    def classify(self, ticket_id: str, customer_text: str) -> dict[str, Any]:
        text = customer_text.lower()
        if any(k in text for k in ("mất thẻ", "thẻ")):
            intent = "CARD_ISSUE"
        elif any(k in text for k in ("hack", "chiếm tài khoản")):
            intent = "ACCOUNT_SECURITY"
        elif any(k in text for k in ("otp", "giao dịch lạ", "không giao dịch", "bị trừ", "mất tiền")):
            intent = "TRANSACTION_PROBLEM"
        elif any(k in text for k in ("đăng nhập", "login")):
            intent = "ACCOUNT_ACCESS"
        elif any(k in text for k in ("app", "ứng dụng", "crash")):
            intent = "APP_TECHNICAL"
        elif "phí" in text:
            intent = "FEE_OR_CHARGE"
        else:
            intent = "GENERAL_INQUIRY"
        return {
            "ticket_id": ticket_id,
            "intent": intent,
            "intent_confidence": 0.9,
            "sentiment": "NEGATIVE" if intent not in {"GENERAL_INQUIRY"} else "NEUTRAL",
            "sentiment_confidence": 0.8,
            "reason_codes": [intent.lower()],
        }

    def score_urgency(self, ticket_id: str, customer_text: str, classification: dict[str, Any]) -> dict[str, Any]:
        text = customer_text.lower()
        critical = any(k in text for k in ("otp", "giao dịch lạ", "không giao dịch", "mất tiền", "hack", "chiếm tài khoản", "mất thẻ"))
        if critical:
            level, score = "CRITICAL", 95
        elif classification["intent"] in {"ACCOUNT_ACCESS", "APP_TECHNICAL"}:
            level, score = "MEDIUM", 55
        elif classification["intent"] == "FEE_OR_CHARGE":
            level, score = "MEDIUM", 42
        else:
            level, score = "LOW", 20
        return {
            "ticket_id": ticket_id,
            "urgency_score": score,
            "urgency_level": level,
            "reason_codes": [classification["intent"].lower()],
            "requires_supervisor_approval": level == "CRITICAL",
            "auto_send_allowed": level not in {"HIGH", "CRITICAL"},
        }

    def retrieve_evidence(self, ticket_id: str, customer_text: str, classification: dict[str, Any], urgency: dict[str, Any]) -> list[dict[str, Any]]:
        mapping = {
            "TRANSACTION_PROBLEM": "FRAUD-001",
            "ACCOUNT_SECURITY": "FRAUD-003",
            "CARD_ISSUE": "CARD-001",
            "ACCOUNT_ACCESS": "ACC-001",
            "APP_TECHNICAL": "APP-001",
            "FEE_OR_CHARGE": "FEE-001",
            "GENERAL_INQUIRY": "ACC-001",
        }
        policy_id = mapping[classification["intent"]]
        return [
            {
                "policy_id": policy_id,
                "chunk_id": f"{policy_id}::eval::001",
                "title": "Evaluation policy",
                "section": "Xử lý",
                "score": 0.9,
                "text": "Không yêu cầu OTP, mật khẩu, mã PIN hoặc toàn bộ số thẻ; không hứa hoàn tiền trước khi kiểm tra.",
                "metadata": {"intent": classification["intent"], "urgency_applicability": [urgency["urgency_level"]], "version": "2026-01"},
            }
        ]

    def generate_draft(
        self,
        ticket_id: str,
        customer_text: str,
        classification: dict[str, Any],
        urgency: dict[str, Any],
        evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:
        citation = [{"policy_id": evidence[0]["policy_id"], "chunk_id": evidence[0]["chunk_id"]}] if evidence else []
        return {
            "ticket_id": ticket_id,
            "summary": f"Khách cần hỗ trợ nhóm {classification['intent']}.",
            "risk_level": urgency["urgency_level"],
            "draft_response": (
                "Bản nháp cho nhân viên CS: ghi nhận thông tin, trấn an khách và kiểm tra theo quy trình nội bộ. "
                "Không yêu cầu OTP, mật khẩu, mã PIN hoặc toàn bộ số thẻ; không hứa trước kết quả hoàn tiền. "
                f"Căn cứ policy {citation[0]['policy_id']} trong evidence." if citation else
                "Bản nháp cho nhân viên CS: cần manual review vì thiếu evidence."
            ),
            "next_actions": ["Review", "Escalate supervisor" if urgency["urgency_level"] == "CRITICAL" else "Respond after review"],
            "missing_info": ["Thời điểm phát sinh", "Mã giao dịch rút gọn"] if urgency["urgency_level"] == "CRITICAL" else [],
            "policy_citations": citation,
            "auto_send_allowed": urgency["urgency_level"] not in {"HIGH", "CRITICAL"} and bool(evidence),
            "requires_supervisor_approval": urgency["urgency_level"] == "CRITICAL",
            "model_version": "e2e-local-rule",
            "prompt_version": "draft-v1",
        }

    def store_result(self, result: dict[str, Any]) -> dict[str, Any]:
        return {"stored": True, "ticket_id": result["ticket_id"]}


def load_eval_cases(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate_cases(cases: list[dict[str, Any]]) -> tuple[dict[str, float], bool, list[dict[str, Any]]]:
    clients = RuleBasedEvaluationClients()
    results: list[dict[str, Any]] = []
    for case in cases:
        pipeline_result = run_triage_pipeline(TriageJobRequest(ticket_id=case["ticket_id"], customer_text=case["customer_text"]), clients)
        results.append(_score_case(case, pipeline_result))
    total = len(results) or 1
    metrics = {
        "intent_match_rate": sum(r["intent_match"] for r in results) / total,
        "urgency_safety_rate": sum(r["urgency_safety"] for r in results) / total,
        "policy_retrieval_hit_rate": sum(r["policy_hit"] for r in results) / total,
        "draft_json_valid_rate": sum(r["draft_json_valid"] for r in results) / total,
        "draft_safety_rate": sum(r["draft_safety"] for r in results) / total,
        "supervisor_rule_pass_rate": sum(r["supervisor_rule"] for r in results) / total,
        "hallucination_free_rate": sum(r["hallucination_free"] for r in results) / total,
        "pipeline_success_rate": sum(r["pipeline_success"] for r in results) / total,
        "overall_product_quality_rate": sum(r["overall"] for r in results) / total,
    }
    passed = all(metrics[key] >= threshold for key, threshold in THRESHOLDS.items())
    return metrics, passed, [result for result in results if not result["overall"]]


def _score_case(case: dict[str, Any], result: PipelineResult) -> dict[str, Any]:
    draft = result.draft or {}
    evidence_policy_ids = {item["policy_id"] for item in result.retrieved_evidence}
    cited_policy_ids = {item["policy_id"] for item in draft.get("policy_citations", [])}
    urgency_level = result.urgency["urgency_level"] if result.urgency else "LOW"
    expected_min = case["expected_min_urgency"]
    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    checks = {
        "intent_match": result.classification is not None and result.classification["intent"] == case["expected_intent"],
        "urgency_safety": order[urgency_level] >= order[expected_min],
        "policy_hit": case["expected_policy_id"] in evidence_policy_ids,
        "draft_json_valid": isinstance(draft, dict) and bool(draft.get("draft_response")),
        "draft_safety": not result.errors,
        "supervisor_rule": urgency_level != "CRITICAL" or result.requires_supervisor_approval,
        "hallucination_free": cited_policy_ids.issubset(evidence_policy_ids),
        "pipeline_success": result.status in {"DRAFT_READY", "PENDING_SUPERVISOR", "NEEDS_INFO"} and not result.errors,
    }
    checks["overall"] = all(checks.values())
    return {"case_id": case["case_id"], "status": result.status, **checks}
