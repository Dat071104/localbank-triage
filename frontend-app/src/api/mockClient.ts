import type { Analysis, AppApi, AuditLog, Draft, DraftResponse, Employee, LoginRequest, LoginResponse, Role, RuntimeStatus, Ticket, UrgencyLevel, ReviewResponse } from "./types";
import { ApiError } from "./client";

interface MockState {
  currentUser: Employee | null;
  tickets: Ticket[];
  analyses: Record<string, Analysis>;
  drafts: Record<string, DraftResponse>;
  audits: Record<string, AuditLog[]>;
  failNext: boolean;
}

const employees: Record<Role, Employee> = {
  CS_AGENT: { employee_id: "cs001", display_name: "Mai Tran", role: "CS_AGENT", department: "Contact Center", branch_code: "HCM" },
  SUPERVISOR: { employee_id: "sup001", display_name: "An Nguyen", role: "SUPERVISOR", department: "Risk Review", branch_code: "HCM" },
  AUDITOR: { employee_id: "aud001", display_name: "Linh Pham", role: "AUDITOR", department: "Internal Audit", branch_code: "HN" },
  ADMIN: { employee_id: "adm001", display_name: "Local Admin", role: "ADMIN", department: "Platform", branch_code: "HQ" }
};

const seedTicket: Ticket = {
  ticket_id: "OTP-CRITICAL-001",
  customer_text: "Khach bao da lo OTP va thay giao dich 25 trieu khong phai do minh thuc hien.",
  status: "DRAFT_READY",
  created_by: "cs001"
};

function defaultState(): MockState {
  const analysis = buildAnalysis(seedTicket);
  const draft = buildDraft(seedTicket.ticket_id, analysis.urgency.urgency_level);
  return {
    currentUser: null,
    tickets: [seedTicket],
    analyses: { [seedTicket.ticket_id]: analysis },
    drafts: { [seedTicket.ticket_id]: { ticket_id: seedTicket.ticket_id, draft } },
    audits: {
      [seedTicket.ticket_id]: [
        audit(seedTicket.ticket_id, "create_ticket", "success", "CS_AGENT"),
        audit(seedTicket.ticket_id, "analyze", "success", "CS_AGENT"),
        audit(seedTicket.ticket_id, "draft", "success", "CS_AGENT")
      ]
    },
    failNext: false
  };
}

let state = defaultState();

export function createMockClient(): AppApi {
  return {
    mode: "mock",
    async login(payload: LoginRequest): Promise<LoginResponse> {
      await pause(120);
      const role = payload.mock_role ?? roleFromEmployee(payload.employee_id);
      const employee = employees[role];
      state.currentUser = employee;
      return { access_token: `mock-${role.toLowerCase()}-token`, employee };
    },
    async logout(): Promise<void> {
      state.currentUser = null;
    },
    async listTickets(): Promise<Ticket[]> {
      requireUser();
      await pause(120);
      return [...state.tickets];
    },
    async createTicket(payload): Promise<Ticket> {
      const user = requireUser();
      assertWrite(user.role);
      await pause(150);
      if (payload.customer_text.includes("SERVICE_FAILURE")) state.failNext = true;
      const ticket = { ticket_id: payload.ticket_id, customer_text: payload.customer_text, status: "NEW", created_by: user.employee_id };
      state.tickets = [ticket, ...state.tickets];
      state.audits[ticket.ticket_id] = [audit(ticket.ticket_id, "create_ticket", "success", user.role)];
      return ticket;
    },
    async getTicket(ticketId: string): Promise<Ticket> {
      requireUser();
      return findTicket(ticketId);
    },
    async analyzeTicket(ticketId: string): Promise<Analysis> {
      const user = requireUser();
      assertWrite(user.role);
      await pause(350);
      if (state.failNext) {
        state.failNext = false;
        throw new ApiError("A downstream service is unavailable. Stage: classifier.", 502, "Retry after checking classifier, urgency, RAG, and LLM services.");
      }
      const ticket = findTicket(ticketId);
      const analysis = buildAnalysis(ticket);
      state.analyses[ticketId] = analysis;
      updateTicket(ticketId, "ANALYZED");
      pushAudit(ticketId, audit(ticketId, "analyze", "success", user.role));
      return analysis;
    },
    async getAnalysis(ticketId: string): Promise<Analysis> {
      requireUser();
      const analysis = state.analyses[ticketId];
      if (!analysis) throw new ApiError("Analysis not found.", 404, "Run analysis first.");
      return analysis;
    },
    async createDraft(ticketId: string): Promise<DraftResponse> {
      const user = requireUser();
      assertWrite(user.role);
      await pause(350);
      const analysis = state.analyses[ticketId] ?? buildAnalysis(findTicket(ticketId));
      const draft = buildDraft(ticketId, analysis.urgency.urgency_level, findTicket(ticketId).customer_text);
      const response = { ticket_id: ticketId, draft };
      state.drafts[ticketId] = response;
      updateTicket(ticketId, "DRAFT_READY");
      pushAudit(ticketId, audit(ticketId, "draft", "success", user.role));
      return response;
    },
    async getDraft(ticketId: string): Promise<DraftResponse> {
      requireUser();
      const draft = state.drafts[ticketId];
      if (!draft) throw new ApiError("Draft not found.", 404, "Generate a draft first.");
      return draft;
    },
    async reviewTicket(ticketId: string, payload): Promise<ReviewResponse> {
      const user = requireUser();
      const draft = normalizeDraft(state.drafts[ticketId]?.draft);
      if (!draft) throw new ApiError("Draft required before review.", 409, "Generate a draft before approving.");
      if (payload.action === "APPROVE" && !canApprove(user.role, draft.risk_level)) {
        pushAudit(ticketId, audit(ticketId, "review_approve", "denied", user.role));
        throw new ApiError("Role cannot approve this ticket risk level.", 403, "Request supervisor approval for HIGH or CRITICAL tickets.");
      }
      if (user.role === "AUDITOR") throw new ApiError("Role is not allowed for this action.", 403, "Auditors are read-only.");
      const status = payload.action === "APPROVE" ? "APPROVED" : payload.action === "REJECT" ? "REJECTED" : "SUPERVISOR_REQUESTED";
      updateTicket(ticketId, status);
      pushAudit(ticketId, audit(ticketId, `review_${payload.action.toLowerCase()}`, "success", user.role));
      return { ticket_id: ticketId, action: payload.action, status };
    },
    async getAudit(ticketId: string): Promise<AuditLog[]> {
      const user = requireUser();
      if (user.role === "CS_AGENT") throw new ApiError("Audit log requires supervisor, auditor, or admin.", 403, "Switch to a supervisor or auditor role.");
      return state.audits[ticketId] ?? [];
    },
    async getRuntimeStatus(): Promise<RuntimeStatus[]> {
      await pause(80);
      return [
        { name: "auth-service", status: "mock", detail: "Mock login is active for local demo." },
        { name: "api-gateway", status: "mock", detail: "Gateway workflow is simulated in browser memory." },
        { name: "postgres", status: "mock", detail: "Persistent workflow storage is mocked." },
        { name: "redis / worker", status: "mock", detail: "Async pipeline progress is simulated step by step." },
        { name: "qdrant / rag-service / llm-service", status: "mock", detail: "Policy evidence and draft guardrails use deterministic fixtures." }
      ];
    },
    resetMock(): void {
      state = defaultState();
    },
    clearMockTickets(): void {
      state.tickets = [];
      state.analyses = {};
      state.drafts = {};
      state.audits = {};
    }
  };
}

function roleFromEmployee(employeeId: string): Role {
  if (employeeId.toLowerCase().startsWith("sup")) return "SUPERVISOR";
  if (employeeId.toLowerCase().startsWith("aud")) return "AUDITOR";
  if (employeeId.toLowerCase().startsWith("adm")) return "ADMIN";
  return "CS_AGENT";
}

function requireUser(): Employee {
  if (!state.currentUser) throw new ApiError("You are not logged in.", 401, "Log in again.");
  return state.currentUser;
}

function assertWrite(role: Role): void {
  if (role === "AUDITOR") throw new ApiError("Role is not allowed for this action.", 403, "Auditors can review evidence but cannot modify workflow state.");
}

function findTicket(ticketId: string): Ticket {
  const ticket = state.tickets.find((item) => item.ticket_id === ticketId);
  if (!ticket) throw new ApiError("Ticket not found.", 404, "Return to the queue and select an existing ticket.");
  return ticket;
}

function updateTicket(ticketId: string, status: string): void {
  state.tickets = state.tickets.map((ticket) => (ticket.ticket_id === ticketId ? { ...ticket, status } : ticket));
}

function buildAnalysis(ticket: Ticket): Analysis {
  const lower = ticket.customer_text.toLowerCase();
  const noPolicy = lower.includes("no_policy") || lower.includes("khong co chinh sach");
  const low = lower.includes("gio lam viec") || lower.includes("lai suat") || lower.includes("LOW_GENERAL");
  const level: UrgencyLevel = low ? "LOW" : lower.includes("the bi nuot") ? "MEDIUM" : lower.includes("SERVICE_FAILURE") ? "HIGH" : "CRITICAL";
  const intent = low ? "GENERAL_INQUIRY" : lower.includes("the") ? "CARD_ISSUE" : "FRAUD_UNAUTHORIZED_TRANSACTION";
  return {
    ticket_id: ticket.ticket_id,
    classification: {
      ticket_id: ticket.ticket_id,
      intent,
      intent_confidence: low ? 0.82 : 0.96,
      sentiment: low ? "neutral" : "negative",
      sentiment_confidence: low ? 0.74 : 0.92,
      model_version: "mock-classifier-1",
      reason_codes: low ? ["general_question"] : ["otp_leak", "unauthorized_transaction"]
    },
    urgency: {
      ticket_id: ticket.ticket_id,
      urgency_score: level === "LOW" ? 18 : level === "MEDIUM" ? 46 : level === "HIGH" ? 74 : 96,
      urgency_level: level,
      reason_codes: level === "CRITICAL" ? ["otp_leak", "money_loss", "account_takeover_risk"] : level === "LOW" ? ["no_financial_loss"] : ["customer_blocked"],
      requires_supervisor_approval: level === "HIGH" || level === "CRITICAL",
      auto_send_allowed: level === "LOW"
    },
    evidence: noPolicy
      ? []
      : [
          {
            policy_id: level === "LOW" ? "ACC-001" : "FRAUD-002",
            chunk_id: level === "LOW" ? "ACC-001#overview" : "FRAUD-002#khong-duoc-lam",
            title: level === "LOW" ? "General account support" : "OTP leakage and unauthorized transaction",
            section: level === "LOW" ? "Customer guidance" : "Không được làm",
            score: level === "LOW" ? 0.78 : 0.94,
            text:
              level === "LOW"
                ? "Provide general guidance and ask for non-sensitive account context if needed."
                : "Không được làm: do not ask for full OTP, PIN, password, or promise refund before investigation. Escalate CRITICAL fraud immediately.",
            metadata: { intent, urgency_applicability: [level], version: "mock" }
          },
          {
            policy_id: "ESC-002",
            chunk_id: "ESC-002#supervisor",
            title: "Supervisor approval",
            section: "Approval control",
            score: 0.88,
            text: "HIGH and CRITICAL cases require supervisor approval before final customer response.",
            metadata: { intent: "ESCALATION", urgency_applicability: ["HIGH", "CRITICAL"], version: "mock" }
          }
        ]
  };
}

function buildDraft(ticketId: string, level: UrgencyLevel, customerText = ""): Draft {
  const noPolicy = customerText.toLowerCase().includes("no_policy");
  const unsafe = customerText.toLowerCase().includes("unsafe_draft");
  return {
    ticket_id: ticketId,
    summary: level === "LOW" ? "General banking inquiry; no fraud indicators." : "Possible OTP leak and unauthorized transaction; supervisor review required.",
    risk_level: level,
    draft_response:
      level === "LOW"
        ? "Cam on anh/chi da lien he. Nhan vien se kiem tra thong tin khong nhay cam va phan hoi huong dan phu hop."
        : "Cam on anh/chi da thong bao. Ngan hang se khoa/kiem tra rui ro theo quy trinh va chuyen giam sat vien xet duyet truoc khi phan hoi tiep.",
    next_actions: level === "LOW" ? ["Confirm non-sensitive request context", "Send reviewed answer"] : ["Lock affected channel if needed", "Escalate to supervisor", "Open fraud investigation case"],
    missing_info: noPolicy ? ["No matching policy evidence; manual review required"] : level === "LOW" ? ["Preferred contact channel"] : ["Transaction timestamp", "Last four digits only", "Customer confirmation of device possession"],
    policy_citations: noPolicy ? [] : [{ policy_id: level === "LOW" ? "ACC-001" : "FRAUD-002", chunk_id: level === "LOW" ? "ACC-001#overview" : "FRAUD-002#khong-duoc-lam" }],
    auto_send_allowed: level === "LOW" && !unsafe,
    requires_supervisor_approval: level === "HIGH" || level === "CRITICAL" || unsafe,
    model_version: "mock-llm-guarded",
    prompt_version: "localbank-draft-v1",
    validation_passed: !unsafe && !noPolicy,
    validation_issues: unsafe ? [{ code: "UNSAFE_DRAFT", message: "Draft was flagged and cannot be sent without supervisor/manual review." }] : noPolicy ? [{ code: "NO_POLICY_CONTEXT", message: "No policy citation was available." }] : [],
    used_fallback: unsafe || noPolicy
  };
}

function normalizeDraft(value: DraftResponse["draft"] | undefined): Draft | null {
  if (!value) return null;
  return "draft" in value ? value.draft : value;
}

function canApprove(role: Role, level: UrgencyLevel): boolean {
  if (role === "ADMIN" || role === "SUPERVISOR") return true;
  if (role === "CS_AGENT") return level === "LOW" || level === "MEDIUM";
  return false;
}

function audit(ticketId: string, action: string, status: string, role: Role): AuditLog {
  const actor = employees[role];
  return {
    ticket_id: ticketId,
    action,
    status,
    actor_employee_id: actor.employee_id,
    actor_role: role,
    details: { source: "mock" }
  };
}

function pushAudit(ticketId: string, item: AuditLog): void {
  state.audits[ticketId] = [...(state.audits[ticketId] ?? []), item];
}

function pause(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
