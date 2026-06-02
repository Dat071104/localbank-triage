export type Role = "CS_AGENT" | "SUPERVISOR" | "AUDITOR" | "ADMIN";
export type UrgencyLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Employee {
  employee_id: string;
  display_name: string;
  role: Role;
  department?: string;
  branch_code?: string;
}

export interface LoginRequest {
  employee_id: string;
  full_name: string;
  access_code: string;
  device_id: string;
  mock_role?: Role;
}

export interface LoginResponse {
  access_token: string;
  employee: Employee;
}

export interface Ticket {
  ticket_id: string;
  customer_text: string;
  status: string;
  created_by: string;
}

export interface Classification {
  ticket_id?: string;
  intent: string;
  intent_confidence: number;
  sentiment: string;
  sentiment_confidence: number;
  model_version?: string;
  reason_codes: string[];
}

export interface Urgency {
  ticket_id?: string;
  urgency_score: number;
  urgency_level: UrgencyLevel;
  reason_codes: string[];
  requires_supervisor_approval: boolean;
  auto_send_allowed: boolean;
}

export interface PolicyEvidence {
  policy_id: string;
  chunk_id: string;
  title?: string;
  section: string;
  score: number;
  text: string;
  metadata?: Record<string, unknown>;
}

export interface Analysis {
  ticket_id: string;
  classification: Classification;
  urgency: Urgency;
  evidence: PolicyEvidence[];
}

export interface Draft {
  ticket_id?: string;
  summary: string;
  risk_level: UrgencyLevel;
  draft_response: string;
  next_actions: string[];
  missing_info: string[];
  policy_citations: Array<{ policy_id: string; chunk_id: string }>;
  auto_send_allowed: boolean;
  requires_supervisor_approval: boolean;
  model_version?: string;
  prompt_version?: string;
  validation_passed?: boolean;
  validation_issues?: Array<{ code: string; message: string }>;
  used_fallback?: boolean;
}

export interface DraftResponse {
  ticket_id: string;
  draft: Draft | { draft: Draft; validation_passed?: boolean; validation_issues?: Array<{ code: string; message: string }>; used_fallback?: boolean };
  edited_draft_response?: string | null;
}

export interface ReviewResponse {
  ticket_id: string;
  action: string;
  status: string;
}

export interface AuditLog {
  ticket_id: string;
  action: string;
  status: string;
  actor_employee_id: string;
  actor_role: Role;
  details: Record<string, unknown>;
}

export interface RuntimeStatus {
  name: string;
  status: "ok" | "offline" | "mock" | "unknown";
  detail: string;
}

export interface AppApi {
  mode: "mock" | "real";
  login(payload: LoginRequest): Promise<LoginResponse>;
  logout(): Promise<void>;
  listTickets(): Promise<Ticket[]>;
  createTicket(payload: { ticket_id: string; customer_text: string }): Promise<Ticket>;
  getTicket(ticketId: string): Promise<Ticket>;
  analyzeTicket(ticketId: string): Promise<Analysis>;
  getAnalysis(ticketId: string): Promise<Analysis>;
  createDraft(ticketId: string): Promise<DraftResponse>;
  getDraft(ticketId: string): Promise<DraftResponse>;
  reviewTicket(ticketId: string, payload: { action: string; comment?: string; edited_draft_response?: string }): Promise<ReviewResponse>;
  getAudit(ticketId: string): Promise<AuditLog[]>;
  getRuntimeStatus(): Promise<RuntimeStatus[]>;
  resetMock?(): void;
}
