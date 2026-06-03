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

const seedTickets: Ticket[] = [
  {
    ticket_id: "OTP-CRITICAL-001",
    display_title: "Lộ OTP và giao dịch không hợp lệ",
    customer_text: "Khách báo đã lộ OTP, sau đó thấy giao dịch 25 triệu đồng không phải do mình thực hiện.",
    status: "DRAFT_READY",
    created_by: "cs001",
    created_at: "2026-06-03 09:12",
    source: "Hotline",
    intent: "FRAUD_UNAUTHORIZED_TRANSACTION",
    urgency_level: "CRITICAL",
    urgency_score: 96
  },
  {
    ticket_id: "CARD-CRITICAL-002",
    display_title: "Mất thẻ và bị trừ tiền",
    customer_text: "Khách bị mất thẻ ghi nợ, vừa nhận SMS trừ 8,5 triệu ở giao dịch lạ, yêu cầu khóa thẻ ngay.",
    status: "PENDING_SUPERVISOR",
    created_by: "cs001",
    created_at: "2026-06-03 09:24",
    source: "Chi nhánh",
    intent: "CARD_FRAUD_LOST_CARD",
    urgency_level: "CRITICAL",
    urgency_score: 94
  },
  {
    ticket_id: "SEC-HIGH-003",
    display_title: "Đăng nhập lạ nghi chiếm quyền tài khoản",
    customer_text: "Khách nhận cảnh báo đăng nhập từ thiết bị lạ ở tỉnh khác, mật khẩu vừa bị đổi và không vào được tài khoản.",
    status: "DRAFT_READY",
    created_by: "cs001",
    created_at: "2026-06-03 09:41",
    source: "Mobile app",
    intent: "ACCOUNT_TAKEOVER",
    urgency_level: "HIGH",
    urgency_score: 82
  },
  {
    ticket_id: "APP-MEDIUM-004",
    display_title: "Không đăng nhập được mobile banking",
    customer_text: "Khách không đăng nhập được ứng dụng mobile banking từ sáng nay, màn hình báo lỗi nhưng không có dấu hiệu giao dịch lạ.",
    status: "NEEDS_INFO",
    created_by: "cs001",
    created_at: "2026-06-03 10:05",
    source: "Chat",
    intent: "APP_LOGIN_FAILURE",
    urgency_level: "MEDIUM",
    urgency_score: 48
  },
  {
    ticket_id: "FEE-LOW-005",
    display_title: "Khiếu nại phí duy trì tài khoản",
    customer_text: "Khách thắc mắc vì bị thu phí duy trì tài khoản tháng này và muốn được giải thích biểu phí.",
    status: "NEW",
    created_by: "cs001",
    created_at: "2026-06-03 10:22",
    source: "Email",
    intent: "FEE_COMPLAINT",
    urgency_level: "LOW",
    urgency_score: 28
  },
  {
    ticket_id: "INFO-LOW-006",
    display_title: "Hỏi thông tin sản phẩm tiết kiệm",
    customer_text: "Khách hỏi giờ làm việc cuối tuần và lãi suất tiết kiệm kỳ hạn 6 tháng, chưa cung cấp thông tin nhạy cảm.",
    status: "DRAFT_READY",
    created_by: "cs001",
    created_at: "2026-06-03 10:37",
    source: "Web form",
    intent: "GENERAL_INQUIRY",
    urgency_level: "LOW",
    urgency_score: 18
  },
  {
    ticket_id: "SAFE-MANUAL-007",
    display_title: "Không có ngữ cảnh chính sách phù hợp",
    customer_text: "no_policy Khách hỏi tình huống đặc biệt chưa có chính sách phù hợp trong kho tri thức, cần kiểm tra thủ công.",
    status: "NEEDS_INFO",
    created_by: "cs001",
    created_at: "2026-06-03 10:51",
    source: "Email",
    intent: "MANUAL_REVIEW_REQUIRED",
    urgency_level: "MEDIUM",
    urgency_score: 52
  }
];

function defaultState(): MockState {
  const analyses = Object.fromEntries(seedTickets.map((ticket) => [ticket.ticket_id, buildAnalysis(ticket)])) as Record<string, Analysis>;
  const drafts = Object.fromEntries(
    seedTickets.map((ticket) => {
      const analysis = analyses[ticket.ticket_id];
      return [ticket.ticket_id, { ticket_id: ticket.ticket_id, draft: buildDraft(ticket.ticket_id, analysis.urgency.urgency_level, ticket.customer_text) }];
    })
  ) as Record<string, DraftResponse>;
  return {
    currentUser: null,
    tickets: seedTickets,
    analyses,
    drafts,
    audits: Object.fromEntries(
      seedTickets.map((ticket) => [
        ticket.ticket_id,
        [audit(ticket.ticket_id, "create_ticket", "success", "CS_AGENT"), audit(ticket.ticket_id, "analyze", "success", "CS_AGENT"), audit(ticket.ticket_id, "draft", "success", "CS_AGENT")]
      ])
    ) as Record<string, AuditLog[]>,
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
      const analysisSeed = buildAnalysis({ ticket_id: payload.ticket_id, customer_text: payload.customer_text, status: "NEW", created_by: user.employee_id });
      const ticket: Ticket = {
        ticket_id: payload.ticket_id,
        display_title: "Ticket khách hàng mới",
        customer_text: payload.customer_text,
        status: "NEW",
        created_by: user.employee_id,
        created_at: new Date().toLocaleString("vi-VN"),
        source: "Demo form",
        intent: analysisSeed.classification.intent,
        urgency_level: analysisSeed.urgency.urgency_level,
        urgency_score: analysisSeed.urgency.urgency_score
      };
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
        throw new ApiError("Dịch vụ phía sau tạm thời không sẵn sàng. Bước lỗi: classifier.", 502, "Kiểm tra classifier, urgency, RAG và LLM rồi thử lại.");
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
      if (!analysis) throw new ApiError("Chưa có kết quả phân tích.", 404, "Hãy chạy phân tích trước.");
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
      if (!draft) throw new ApiError("Chưa có bản nháp.", 404, "Hãy tạo bản nháp trước.");
      return draft;
    },
    async reviewTicket(ticketId: string, payload): Promise<ReviewResponse> {
      const user = requireUser();
      const draft = normalizeDraft(state.drafts[ticketId]?.draft);
      if (!draft) throw new ApiError("Cần có bản nháp trước khi duyệt.", 409, "Hãy tạo bản nháp trước khi phê duyệt.");
      if (payload.action === "APPROVE" && draft.validation_passed === false) {
        pushAudit(ticketId, audit(ticketId, "review_approve", "denied", user.role));
        throw new ApiError("Bản nháp chưa đạt kiểm tra an toàn.", 403, "Cần kiểm tra thủ công hoặc bổ sung bằng chứng chính sách trước khi duyệt.");
      }
      if (payload.action === "APPROVE" && !canApprove(user.role, draft.risk_level)) {
        pushAudit(ticketId, audit(ticketId, "review_approve", "denied", user.role));
        throw new ApiError("Vai trò này không thể duyệt mức rủi ro của ticket.", 403, "Yêu cầu supervisor phê duyệt với ticket HIGH hoặc CRITICAL.");
      }
      if (user.role === "AUDITOR") throw new ApiError("Vai trò này không được phép thực hiện thao tác.", 403, "AUDITOR chỉ được xem.");
      const status = payload.action === "APPROVE" ? "APPROVED" : payload.action === "REJECT" ? "REJECTED" : "SUPERVISOR_REQUESTED";
      updateTicket(ticketId, status);
      pushAudit(ticketId, audit(ticketId, `review_${payload.action.toLowerCase()}`, "success", user.role));
      return { ticket_id: ticketId, action: payload.action, status };
    },
    async getAudit(ticketId: string): Promise<AuditLog[]> {
      const user = requireUser();
      if (user.role === "CS_AGENT") throw new ApiError("Lịch sử kiểm tra yêu cầu supervisor, auditor hoặc admin.", 403, "Chuyển sang vai trò supervisor hoặc auditor.");
      return state.audits[ticketId] ?? [];
    },
    async getRuntimeStatus(): Promise<RuntimeStatus[]> {
      await pause(80);
      return [
        { name: "auth-service", status: "mock", detail: "Đăng nhập demo đang chạy local trong trình duyệt." },
        { name: "api-gateway", status: "mock", detail: "Luồng xử lý gateway được mô phỏng trong bộ nhớ trình duyệt." },
        { name: "postgres", status: "mock", detail: "Lưu trữ trạng thái workflow đang dùng dữ liệu demo." },
        { name: "redis / worker", status: "mock", detail: "Tiến trình bất đồng bộ được mô phỏng từng bước." },
        { name: "qdrant / rag-service / llm-service", status: "mock", detail: "Bằng chứng chính sách và guardrail bản nháp dùng fixture xác định." }
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
  if (!state.currentUser) throw new ApiError("Bạn chưa đăng nhập.", 401, "Đăng nhập lại.");
  return state.currentUser;
}

function assertWrite(role: Role): void {
  if (role === "AUDITOR") throw new ApiError("Vai trò này không được phép thực hiện thao tác.", 403, "AUDITOR có thể xem bằng chứng nhưng không thể thay đổi trạng thái workflow.");
}

function findTicket(ticketId: string): Ticket {
  const ticket = state.tickets.find((item) => item.ticket_id === ticketId);
  if (!ticket) throw new ApiError("Không tìm thấy ticket.", 404, "Quay lại hàng đợi và chọn một ticket hiện có.");
  return ticket;
}

function updateTicket(ticketId: string, status: string): void {
  state.tickets = state.tickets.map((ticket) => (ticket.ticket_id === ticketId ? { ...ticket, status } : ticket));
}

function buildAnalysis(ticket: Ticket): Analysis {
  const lower = ticket.customer_text.toLowerCase();
  const noPolicy = lower.includes("no_policy") || lower.includes("khong co chinh sach");
  const level = detectUrgency(ticket);
  const intent = detectIntent(ticket);
  const low = level === "LOW";
  const medium = level === "MEDIUM";
  const fraud = intent.includes("FRAUD") || intent === "ACCOUNT_TAKEOVER";
  const policy = policyForIntent(intent);
  return {
    ticket_id: ticket.ticket_id,
    classification: {
      ticket_id: ticket.ticket_id,
      intent,
      intent_confidence: fraud ? 0.97 : medium ? 0.86 : 0.82,
      sentiment: fraud ? "negative" : low ? "neutral" : "concerned",
      sentiment_confidence: fraud ? 0.92 : 0.78,
      model_version: "mock-classifier-1",
      reason_codes: reasonCodesForIntent(intent)
    },
    urgency: {
      ticket_id: ticket.ticket_id,
      urgency_score: ticket.urgency_score ?? (level === "LOW" ? 18 : level === "MEDIUM" ? 52 : level === "HIGH" ? 82 : 96),
      urgency_level: level,
      reason_codes:
        level === "CRITICAL"
          ? ["money_loss", "active_fraud_signal", "immediate_customer_impact"]
          : level === "HIGH"
            ? ["account_takeover_risk", "security_event"]
            : level === "MEDIUM"
              ? ["customer_blocked", noPolicy ? "missing_policy_context" : "needs_more_info"]
              : ["no_financial_loss", "routine_service_request"],
      requires_supervisor_approval: level === "HIGH" || level === "CRITICAL",
      auto_send_allowed: level === "LOW"
    },
    evidence: noPolicy
      ? []
      : [
          {
            policy_id: policy.policy_id,
            chunk_id: policy.chunk_id,
            title: policy.title,
            section: policy.section,
            score: fraud ? 0.94 : medium ? 0.84 : 0.78,
            text: policy.text,
            metadata: { intent, urgency_applicability: [level], version: "mock" }
          },
          {
            policy_id: "ESC-002",
            chunk_id: "ESC-002#supervisor",
            title: "Quy tắc phê duyệt supervisor",
            section: "Kiểm soát phê duyệt",
            score: 0.88,
            text: "Ticket HIGH và CRITICAL cần supervisor phê duyệt trước phản hồi cuối cùng cho khách hàng.",
            metadata: { intent: "ESCALATION", urgency_applicability: ["HIGH", "CRITICAL"], version: "mock" }
          }
        ]
  };
}

function buildDraft(ticketId: string, level: UrgencyLevel, customerText = ""): Draft {
  const noPolicy = customerText.toLowerCase().includes("no_policy");
  const unsafe = customerText.toLowerCase().includes("unsafe_draft");
  const intent = detectIntent({ customer_text: customerText });
  const policy = policyForIntent(intent);
  const appLogin = intent === "APP_LOGIN_FAILURE";
  const low = level === "LOW";
  return {
    ticket_id: ticketId,
    summary: low
      ? "Câu hỏi dịch vụ ngân hàng thông thường, chưa có dấu hiệu gian lận."
      : appLogin
        ? "Khách không đăng nhập được ứng dụng; cần bổ sung thiết bị, thời điểm và thông báo lỗi."
        : "Có dấu hiệu rủi ro bảo mật/gian lận; cần kiểm tra nâng cao trước khi phản hồi.",
    risk_level: level,
    draft_response:
      low
        ? "Cảm ơn anh/chị đã liên hệ. Ngân hàng sẽ kiểm tra thông tin không nhạy cảm và phản hồi hướng dẫn phù hợp."
        : appLogin
          ? "Cảm ơn anh/chị đã thông báo. Vui lòng cung cấp loại thiết bị, thời điểm phát sinh lỗi và nội dung thông báo lỗi để ngân hàng kiểm tra."
          : "Cảm ơn anh/chị đã thông báo. Ngân hàng sẽ khóa/kiểm tra rủi ro theo quy trình và chuyển supervisor xét duyệt trước khi phản hồi tiếp.",
    next_actions: low
      ? ["Xác nhận nhu cầu không nhạy cảm", "Gửi câu trả lời đã kiểm tra"]
      : appLogin
        ? ["Hỏi loại thiết bị", "Hỏi thời điểm lỗi", "Hỏi thông báo lỗi hiển thị"]
        : ["Khóa kênh bị ảnh hưởng nếu cần", "Chuyển supervisor", "Mở hồ sơ điều tra gian lận"],
    missing_info: noPolicy
      ? ["Không có bằng chứng chính sách phù hợp; cần kiểm tra thủ công"]
      : low
        ? ["Kênh liên hệ mong muốn"]
        : appLogin
          ? ["Loại thiết bị", "Thời điểm phát sinh lỗi", "Thông báo lỗi cụ thể"]
          : ["Thời điểm giao dịch", "Chỉ 4 số cuối thẻ/tài khoản", "Xác nhận khách còn giữ thiết bị"],
    policy_citations: noPolicy ? [] : [{ policy_id: policy.policy_id, chunk_id: policy.chunk_id }],
    auto_send_allowed: low && !unsafe,
    requires_supervisor_approval: level === "HIGH" || level === "CRITICAL" || unsafe || noPolicy,
    model_version: "mock-llm-guarded",
    prompt_version: "localbank-draft-v1",
    validation_passed: !unsafe && !noPolicy,
    validation_issues: unsafe
      ? [{ code: "UNSAFE_DRAFT", message: "Bản nháp bị guardrail chặn và không thể gửi nếu chưa kiểm tra thủ công." }]
      : noPolicy
        ? [{ code: "NO_POLICY_CONTEXT", message: "Không có trích dẫn chính sách phù hợp." }]
        : [],
    used_fallback: unsafe || noPolicy
  };
}

function detectUrgency(ticket: Ticket): UrgencyLevel {
  if (ticket.urgency_level) return ticket.urgency_level;
  const lower = ticket.customer_text.toLowerCase();
  if (lower.includes("gio lam viec") || lower.includes("lãi suất") || lower.includes("lai suat") || lower.includes("phí") || lower.includes("phi") || lower.includes("LOW_GENERAL")) return "LOW";
  if (lower.includes("không đăng nhập") || lower.includes("khong dang nhap") || lower.includes("no_policy")) return "MEDIUM";
  if (lower.includes("thiết bị lạ") || lower.includes("thiet bi la") || lower.includes("đổi mật khẩu") || lower.includes("doi mat khau") || lower.includes("SERVICE_FAILURE")) return "HIGH";
  return "CRITICAL";
}

function detectIntent(ticket: Pick<Ticket, "customer_text" | "intent">): string {
  if (ticket.intent) return ticket.intent;
  const lower = ticket.customer_text.toLowerCase();
  if (lower.includes("no_policy")) return "MANUAL_REVIEW_REQUIRED";
  if (lower.includes("không đăng nhập") || lower.includes("khong dang nhap")) return "APP_LOGIN_FAILURE";
  if (lower.includes("phí") || lower.includes("phi")) return "FEE_COMPLAINT";
  if (lower.includes("giờ làm việc") || lower.includes("gio lam viec") || lower.includes("lãi suất") || lower.includes("lai suat")) return "GENERAL_INQUIRY";
  if (lower.includes("thiết bị lạ") || lower.includes("thiet bi la") || lower.includes("đổi mật khẩu") || lower.includes("doi mat khau")) return "ACCOUNT_TAKEOVER";
  if (lower.includes("mất thẻ") || lower.includes("mat the")) return "CARD_FRAUD_LOST_CARD";
  return "FRAUD_UNAUTHORIZED_TRANSACTION";
}

function reasonCodesForIntent(intent: string): string[] {
  const codes: Record<string, string[]> = {
    FRAUD_UNAUTHORIZED_TRANSACTION: ["otp_leak", "unauthorized_transaction", "money_loss"],
    CARD_FRAUD_LOST_CARD: ["lost_card", "unauthorized_card_transaction", "money_loss"],
    ACCOUNT_TAKEOVER: ["suspicious_login", "password_changed", "account_takeover_risk"],
    APP_LOGIN_FAILURE: ["login_failure", "missing_device_info", "missing_error_message"],
    FEE_COMPLAINT: ["fee_complaint", "no_fraud_signal"],
    GENERAL_INQUIRY: ["general_question", "no_financial_loss"],
    MANUAL_REVIEW_REQUIRED: ["missing_policy_context", "manual_review_required"]
  };
  return codes[intent] ?? ["customer_request"];
}

function policyForIntent(intent: string) {
  const policies: Record<string, { policy_id: string; chunk_id: string; title: string; section: string; text: string }> = {
    FRAUD_UNAUTHORIZED_TRANSACTION: {
      policy_id: "FRAUD-002",
      chunk_id: "FRAUD-002#otp-giao-dich",
      title: "Xử lý lộ OTP và giao dịch không hợp lệ",
      section: "Không được làm",
      text: "Không hỏi lại toàn bộ OTP, PIN hoặc mật khẩu; không hứa hoàn tiền trước khi điều tra; escalate CRITICAL fraud ngay."
    },
    CARD_FRAUD_LOST_CARD: {
      policy_id: "CARD-004",
      chunk_id: "CARD-004#lost-card-fraud",
      title: "Mất thẻ và giao dịch nghi gian lận",
      section: "Khóa thẻ và điều tra",
      text: "Khóa thẻ ngay, ghi nhận thời điểm giao dịch nghi ngờ, chỉ hỏi thông tin định danh không nhạy cảm và chuyển supervisor với dấu hiệu mất tiền."
    },
    ACCOUNT_TAKEOVER: {
      policy_id: "SEC-003",
      chunk_id: "SEC-003#account-takeover",
      title: "Đăng nhập bất thường và chiếm quyền tài khoản",
      section: "Kiểm tra bảo mật tài khoản",
      text: "Với cảnh báo đăng nhập lạ hoặc đổi mật khẩu không do khách thực hiện, tạm khóa kênh rủi ro và yêu cầu kiểm tra nâng cao."
    },
    APP_LOGIN_FAILURE: {
      policy_id: "APP-001",
      chunk_id: "APP-001#login-support",
      title: "Hỗ trợ lỗi đăng nhập mobile banking",
      section: "Thu thập thông tin lỗi",
      text: "Không coi là gian lận nếu không có dấu hiệu bảo mật; hỏi loại thiết bị, thời điểm lỗi và thông báo lỗi để khoanh vùng."
    },
    FEE_COMPLAINT: {
      policy_id: "FEE-001",
      chunk_id: "FEE-001#fee-explanation",
      title: "Giải thích biểu phí tài khoản",
      section: "Phản hồi khiếu nại phí",
      text: "Giải thích biểu phí công khai, kiểm tra thông tin không nhạy cảm và hướng dẫn khách đối soát nếu cần."
    },
    GENERAL_INQUIRY: {
      policy_id: "ACC-001",
      chunk_id: "ACC-001#overview",
      title: "Hỗ trợ thông tin tài khoản và sản phẩm",
      section: "Hướng dẫn khách hàng",
      text: "Cung cấp thông tin chung và chỉ hỏi thêm ngữ cảnh không nhạy cảm khi cần."
    }
  };
  return policies[intent] ?? policies.GENERAL_INQUIRY;
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
