from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class GatewayEvalMetrics:
    rbac_pass_rate: float
    workflow_state_pass_rate: float
    audit_log_pass_rate: float
    service_failure_handling_rate: float
    critical_safety_pass_rate: float
    overall_pass_rate: float


THRESHOLDS = {
    "rbac_pass_rate": 1.0,
    "critical_safety_pass_rate": 1.0,
    "audit_log_pass_rate": 0.95,
    "workflow_state_pass_rate": 0.95,
    "service_failure_handling_rate": 0.90,
    "overall_pass_rate": 0.95,
}


def calculate_metrics(results: list[dict]) -> tuple[GatewayEvalMetrics, bool]:
    total = len(results) or 1
    metrics = GatewayEvalMetrics(
        rbac_pass_rate=sum(1 for result in results if result.get("rbac_pass")) / total,
        workflow_state_pass_rate=sum(1 for result in results if result.get("workflow_state_pass")) / total,
        audit_log_pass_rate=sum(1 for result in results if result.get("audit_log_pass")) / total,
        service_failure_handling_rate=sum(1 for result in results if result.get("service_failure_handling_pass")) / total,
        critical_safety_pass_rate=sum(1 for result in results if result.get("critical_safety_pass")) / total,
        overall_pass_rate=sum(1 for result in results if all(result.get(key) for key in result if key.endswith("_pass"))) / total,
    )
    values = asdict(metrics)
    passed = all(values[key] >= threshold for key, threshold in THRESHOLDS.items())
    return metrics, passed
