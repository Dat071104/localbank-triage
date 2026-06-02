from __future__ import annotations

import json
from abc import ABC, abstractmethod

import httpx

from .config import LLMConfig
from .schemas import DraftGenerateRequest


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, payload: DraftGenerateRequest) -> str:
        raise NotImplementedError


class FakeLLMClient(LLMClient):
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, prompt: str, payload: DraftGenerateRequest) -> str:
        first_policy = payload.policy_context[0] if payload.policy_context else None
        citations = []
        if first_policy is not None:
            citations.append({"policy_id": first_policy.policy_id, "chunk_id": first_policy.chunk_id})

        missing_info = ["Thời điểm phát sinh sự việc", "Mã giao dịch hoặc bốn số cuối thẻ nếu khách có thể cung cấp"]
        if payload.urgency.urgency_level in {"LOW", "MEDIUM"} and payload.policy_context:
            missing_info = []
        if not payload.policy_context:
            missing_info = ["Cần bổ sung policy_context phù hợp trước khi gửi phản hồi cho khách"]

        risk = payload.urgency.urgency_level
        auto_send = payload.urgency.auto_send_allowed and risk not in {"HIGH", "CRITICAL"} and bool(payload.policy_context)
        supervisor = payload.urgency.requires_supervisor_approval or risk == "CRITICAL" or not payload.policy_context

        draft_response = (
            "Chúng tôi đã ghi nhận trường hợp của khách và sẽ chuyển thông tin cho nhân viên phụ trách kiểm tra theo "
            "quy trình nội bộ. Vui lòng trấn an khách không chia sẻ OTP, mật khẩu, mã PIN hoặc toàn bộ số thẻ. "
            "Nếu cần bổ sung thông tin, chỉ đề nghị khách cung cấp thời điểm phát sinh, kênh giao dịch và mã giao dịch "
            "ở mức không nhạy cảm để hỗ trợ đối soát."
        )
        if risk == "CRITICAL":
            draft_response += " Do mức rủi ro CRITICAL, bản nháp cần supervisor duyệt trước khi phản hồi."
        elif risk in {"LOW", "MEDIUM"}:
            draft_response += " Nội dung phản hồi giữ giọng điệu lịch sự, trung lập và không hứa trước kết quả xử lý."
        if first_policy is not None:
            draft_response += f" Căn cứ policy {first_policy.policy_id} trong context được cung cấp."

        output = {
            "ticket_id": payload.ticket_id,
            "summary": _summarize(payload.customer_text, risk),
            "risk_level": risk,
            "draft_response": draft_response,
            "next_actions": _next_actions(risk, bool(payload.policy_context)),
            "missing_info": missing_info,
            "policy_citations": citations,
            "auto_send_allowed": auto_send,
            "requires_supervisor_approval": supervisor,
            "model_version": self.config.model_version,
            "prompt_version": self.config.prompt_version,
        }
        return json.dumps(output, ensure_ascii=False)


class OllamaLLMClient(LLMClient):
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, prompt: str, payload: DraftGenerateRequest) -> str:
        response = httpx.post(
            f"{self.config.local_base_url}/api/generate",
            json={
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_output_tokens,
                },
            },
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        return str(response.json().get("response", ""))


class LlamaCppLLMClient(LLMClient):
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, prompt: str, payload: DraftGenerateRequest) -> str:
        response = httpx.post(
            f"{self.config.local_base_url}/completion",
            json={
                "prompt": prompt,
                "temperature": self.config.temperature,
                "n_predict": self.config.max_output_tokens,
            },
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        return str(response.json().get("content", ""))


def build_llm_client(config: LLMConfig) -> LLMClient:
    if config.backend == "fake":
        return FakeLLMClient(config)
    if config.backend == "ollama":
        return OllamaLLMClient(config)
    if config.backend in {"llama_cpp", "llamacpp"}:
        return LlamaCppLLMClient(config)
    raise ValueError(f"Unsupported LLM_BACKEND: {config.backend}")


def _summarize(customer_text: str, risk: str) -> str:
    compact = " ".join(customer_text.split())
    if len(compact) > 140:
        compact = compact[:137].rstrip() + "..."
    return f"Khách báo sự việc mức {risk}: {compact}"


def _next_actions(risk: str, has_context: bool) -> list[str]:
    actions = ["Ghi nhận ticket và kiểm tra theo quy trình nội bộ", "Không yêu cầu khách cung cấp thông tin xác thực nhạy cảm"]
    if not has_context:
        actions.append("Chuyển manual review vì chưa có policy_context")
    if risk == "CRITICAL":
        actions.append("Chuyển supervisor kiểm tra và phê duyệt trước khi phản hồi")
    elif risk == "HIGH":
        actions.append("Giữ auto_send_allowed=false và yêu cầu nhân viên duyệt thủ công")
    return actions

