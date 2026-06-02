import type { AppApi, AuditLog, DraftResponse, LoginRequest, LoginResponse, RuntimeStatus, Ticket, Analysis, ReviewResponse } from "./types";
import { createMockClient } from "./mockClient";

const gatewayBaseUrl = import.meta.env.VITE_GATEWAY_BASE_URL ?? "http://localhost:8005";
const authBaseUrl = import.meta.env.VITE_AUTH_SERVICE_URL ?? "http://localhost:8000";
const apiMode = (import.meta.env.VITE_API_MODE ?? "mock").toLowerCase();

export class ApiError extends Error {
  status: number;
  recovery: string;

  constructor(message: string, status = 0, recovery = "Check Local Runtime Status and retry the action.") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.recovery = recovery;
  }
}

async function fetchJson<T>(url: string, options: RequestInit = {}, timeoutMs = 12_000): Promise<T> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {})
      }
    });
    const json = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = json?.error?.message ?? json?.detail ?? "Request failed.";
      const stage = json?.error?.stage ? ` Stage: ${json.error.stage}.` : "";
      throw new ApiError(`${message}${stage}`, response.status);
    }
    return json as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("The local service did not respond before the timeout.", 0, "Confirm the backend stack is running, then retry.");
    }
    throw new ApiError("Cannot reach the local backend service.", 0, "Start the LocalBank services or switch to mock mode.");
  } finally {
    window.clearTimeout(timer);
  }
}

class RealClient implements AppApi {
  mode: "real" = "real";
  private token: string | null = null;

  async login(payload: LoginRequest): Promise<LoginResponse> {
    const result = await fetchJson<LoginResponse>(`${authBaseUrl}/auth/login`, {
      method: "POST",
      body: JSON.stringify({
        employee_id: payload.employee_id,
        full_name: payload.full_name,
        access_code: payload.access_code,
        device_id: payload.device_id
      })
    });
    this.token = result.access_token;
    return result;
  }

  async logout(): Promise<void> {
    if (this.token) {
      await fetchJson(`${authBaseUrl}/auth/logout`, { method: "POST", headers: this.authHeaders() }).catch(() => undefined);
    }
    this.token = null;
  }

  listTickets(): Promise<Ticket[]> {
    return fetchJson<Ticket[]>(`${gatewayBaseUrl}/tickets`, { headers: this.authHeaders() });
  }

  createTicket(payload: { ticket_id: string; customer_text: string }): Promise<Ticket> {
    return fetchJson<Ticket>(`${gatewayBaseUrl}/tickets`, { method: "POST", headers: this.authHeaders(), body: JSON.stringify(payload) });
  }

  getTicket(ticketId: string): Promise<Ticket> {
    return fetchJson<Ticket>(`${gatewayBaseUrl}/tickets/${encodeURIComponent(ticketId)}`, { headers: this.authHeaders() });
  }

  analyzeTicket(ticketId: string): Promise<Analysis> {
    return fetchJson<Analysis>(`${gatewayBaseUrl}/tickets/${encodeURIComponent(ticketId)}/analyze`, { method: "POST", headers: this.authHeaders() }, 25_000);
  }

  getAnalysis(ticketId: string): Promise<Analysis> {
    return fetchJson<Analysis>(`${gatewayBaseUrl}/tickets/${encodeURIComponent(ticketId)}/analysis`, { headers: this.authHeaders() });
  }

  createDraft(ticketId: string): Promise<DraftResponse> {
    return fetchJson<DraftResponse>(`${gatewayBaseUrl}/tickets/${encodeURIComponent(ticketId)}/draft`, { method: "POST", headers: this.authHeaders() }, 30_000);
  }

  getDraft(ticketId: string): Promise<DraftResponse> {
    return fetchJson<DraftResponse>(`${gatewayBaseUrl}/tickets/${encodeURIComponent(ticketId)}/draft`, { headers: this.authHeaders() });
  }

  reviewTicket(ticketId: string, payload: { action: string; comment?: string; edited_draft_response?: string }): Promise<ReviewResponse> {
    return fetchJson<ReviewResponse>(`${gatewayBaseUrl}/tickets/${encodeURIComponent(ticketId)}/review`, {
      method: "POST",
      headers: this.authHeaders(),
      body: JSON.stringify(payload)
    });
  }

  getAudit(ticketId: string): Promise<AuditLog[]> {
    return fetchJson<AuditLog[]>(`${gatewayBaseUrl}/tickets/${encodeURIComponent(ticketId)}/audit`, { headers: this.authHeaders() });
  }

  async getRuntimeStatus(): Promise<RuntimeStatus[]> {
    const checks = await Promise.allSettled([
      fetchJson<{ status: string }>(`${authBaseUrl}/health`, {}, 4_000),
      fetchJson<{ status: string }>(`${gatewayBaseUrl}/health`, {}, 4_000)
    ]);
    return [
      statusFromResult("auth-service", checks[0]),
      statusFromResult("api-gateway", checks[1]),
      { name: "postgres/redis/qdrant/llm", status: "unknown", detail: "Checked through gateway workflow calls; start the Docker stack for real mode." }
    ];
  }

  private authHeaders(): HeadersInit {
    if (!this.token) throw new ApiError("You are not logged in.", 401, "Log in again.");
    return { Authorization: `Bearer ${this.token}` };
  }
}

function statusFromResult(name: string, result: PromiseSettledResult<{ status: string }>): RuntimeStatus {
  if (result.status === "fulfilled" && result.value.status === "ok") {
    return { name, status: "ok", detail: "Reachable on localhost." };
  }
  return { name, status: "offline", detail: "Not reachable from the frontend runtime." };
}

export function createApiClient(): AppApi {
  return apiMode === "real" ? new RealClient() : createMockClient();
}
