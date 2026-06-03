import { createContext, useContext, useMemo, useState } from "react";
import type { Role, UrgencyLevel } from "./api/types";

export type Language = "vi" | "en";

interface I18nContextValue {
  language: Language;
  setLanguage(language: Language): void;
  t(key: TranslationKey): string;
}

const storageKey = "localbank_language";

const translations = {
  vi: {
    "app.product": "LocalBank Triage",
    "nav.queue": "Hàng đợi ticket",
    "nav.workspace": "Không gian xử lý",
    "nav.audit": "Lịch sử kiểm tra",
    "nav.runtime": "Trạng thái hệ thống",
    "nav.aria": "Điều hướng chính",
    "language.label": "Ngôn ngữ",
    "session.mode": "Chế độ",
    "session.ticket": "Ticket",
    "session.logout": "Đăng xuất",
    "login.eyebrow": "Truy cập nội bộ local-first",
    "login.supporting": "Không gian xử lý ticket ngân hàng, bằng chứng chính sách, bản nháp phản hồi và kiểm soát phê duyệt.",
    "login.mockRole": "Vai trò demo",
    "login.employeeId": "Mã nhân viên",
    "login.fullName": "Họ và tên",
    "login.accessCode": "Mã truy cập",
    "login.submit": "Vào không gian xử lý",
    "login.submitting": "Đang kiểm tra phiên local...",
    "login.required": "Cần nhập mã nhân viên, họ tên và mã truy cập.",
    "login.failed": "Đăng nhập thất bại.",
    "queue.eyebrow": "Hàng đợi",
    "queue.refresh": "Tải lại hàng đợi",
    "queue.clear": "Xóa hàng đợi demo",
    "queue.readonly": "Vai trò AUDITOR chỉ được xem và không thể tạo ticket.",
    "queue.newTicket": "Ticket khách hàng mới",
    "queue.create": "Tạo ticket",
    "queue.loading": "Đang tải hàng đợi local...",
    "queue.emptyTitle": "Không có ticket trong hàng đợi",
    "queue.emptyBody": "Tạo ticket để bắt đầu xử lý local, hoặc chuyển sang chế độ real sau khi khởi động backend.",
    "queue.listAria": "Danh sách ticket",
    "queue.open": "Mở ticket",
    "queue.created": "Tạo lúc",
    "queue.source": "Nguồn",
    "queue.intent": "Ý định",
    "queue.loadError": "Không thể tải danh sách ticket.",
    "queue.createError": "Không thể tạo ticket.",
    "workspace.eyebrow": "Xử lý",
    "workspace.title": "Không gian xử lý ticket",
    "workspace.reload": "Tải lại",
    "workspace.readonly": "Chỉ được xem",
    "workspace.run": "Phân tích và tạo bản nháp",
    "workspace.running": "Đang chạy pipeline local...",
    "workspace.noTicketTitle": "Chưa chọn ticket",
    "workspace.noTicketBody": "Mở một ticket từ hàng đợi để bắt đầu xử lý.",
    "workspace.loadTicketError": "Không thể tải ticket.",
    "workspace.pipelineError": "Pipeline xử lý thất bại.",
    "workspace.reviewError": "Thao tác duyệt thất bại.",
    "workspace.reviewRecorded": "đã được ghi nhận. Trạng thái",
    "workspace.customerTicket": "Ticket khách hàng",
    "workspace.status": "Trạng thái",
    "workspace.ticket": "Ticket",
    "workspace.intentUrgency": "Ý định và mức độ khẩn cấp",
    "workspace.confidence": "Độ tin cậy",
    "workspace.sentiment": "Cảm xúc",
    "workspace.policyEvidence": "Bằng chứng chính sách",
    "workspace.noPolicyTitle": "Không có chính sách phù hợp",
    "workspace.noPolicyBody": "Cần kiểm tra thủ công vì không truy xuất được ngữ cảnh chính sách đáng tin cậy.",
    "workspace.policyEmpty": "Chạy phân tích để truy xuất bằng chứng chính sách.",
    "workspace.loadingTicket": "Đang tải ticket...",
    "draft.empty": "Tạo bản nháp sau khi phân tích để kiểm tra nội dung phản hồi khách hàng.",
    "draft.aria": "Kiểm tra bản nháp",
    "draft.title": "Bản nháp chờ người duyệt",
    "draft.supervisorRequired": "Cần supervisor phê duyệt trước khi bản nháp này được duyệt.",
    "draft.validationFailed": "Kiểm tra an toàn bản nháp thất bại. Chặn phê duyệt cho đến khi hoàn tất kiểm tra thủ công.",
    "draft.editor": "Trình soạn bản nháp",
    "draft.missingInfo": "Thông tin còn thiếu",
    "draft.nextActions": "Hành động tiếp theo",
    "draft.citations": "Trích dẫn chính sách",
    "draft.safetyIssues": "Vấn đề an toàn",
    "draft.approve": "Duyệt bản nháp đã kiểm tra",
    "draft.requestSupervisor": "Yêu cầu supervisor duyệt",
    "draft.reject": "Từ chối bản nháp",
    "draft.auditorReadonly": "Vai trò AUDITOR chỉ được xem.",
    "draft.approvalBlocked": "Vai trò này không thể duyệt mức rủi ro này hoặc bản nháp chưa đạt kiểm tra an toàn.",
    "policy.score": "điểm",
    "policy.defaultTitle": "Bằng chứng chính sách",
    "policy.doNot": "Không được làm",
    "pipeline.aria": "Tiến trình xử lý",
    "pipeline.done": "Hoàn tất",
    "pipeline.running": "Đang chạy",
    "pipeline.waiting": "Chờ",
    "pipeline.classify": "Đang phân loại ý định...",
    "pipeline.urgency": "Đang chấm mức độ khẩn cấp...",
    "pipeline.policies": "Đang truy xuất chính sách...",
    "pipeline.draft": "Đang tạo bản nháp cục bộ...",
    "pipeline.safety": "Đang kiểm tra an toàn bản nháp...",
    "pipeline.save": "Đang lưu trạng thái xử lý...",
    "audit.eyebrow": "Kiểm tra",
    "audit.title": "Lịch sử kiểm tra",
    "audit.loadError": "Không thể tải lịch sử kiểm tra.",
    "audit.noTicketTitle": "Chưa chọn ticket",
    "audit.noTicketBody": "Mở một ticket trước khi xem lịch sử kiểm tra.",
    "audit.emptyTitle": "Chưa có bản ghi kiểm tra",
    "audit.emptyBody": "Ticket này chưa có bản ghi kiểm tra hiển thị.",
    "runtime.eyebrow": "Hệ thống local",
    "runtime.title": "Trạng thái hệ thống",
    "runtime.check": "Kiểm tra lại",
    "runtime.loadError": "Không thể kiểm tra trạng thái hệ thống.",
    "runtime.realMode": "Khởi động chế độ real",
    "error.recovery": "Kiểm tra trạng thái hệ thống local rồi thử lại.",
    "status.DRAFT_READY": "BẢN NHÁP SẴN SÀNG",
    "status.PENDING_SUPERVISOR": "CHỜ SUPERVISOR DUYỆT",
    "status.SUPERVISOR_REQUESTED": "ĐÃ YÊU CẦU SUPERVISOR",
    "status.APPROVED": "ĐÃ DUYỆT",
    "status.NEEDS_INFO": "CẦN THÊM THÔNG TIN",
    "status.FAILED": "THẤT BẠI",
    "status.NEW": "MỚI",
    "status.ANALYZED": "ĐÃ PHÂN TÍCH",
    "status.REJECTED": "ĐÃ TỪ CHỐI",
    "urgency.LOW": "THẤP - thông thường",
    "urgency.MEDIUM": "TRUNG BÌNH - theo dõi",
    "urgency.HIGH": "CAO - cần supervisor kiểm tra",
    "urgency.CRITICAL": "RẤT KHẨN CẤP - cần supervisor",
    "role.CS_AGENT": "CS_AGENT",
    "role.SUPERVISOR": "SUPERVISOR",
    "role.AUDITOR": "AUDITOR",
    "role.ADMIN": "ADMIN"
  },
  en: {
    "app.product": "LocalBank Triage",
    "nav.queue": "Ticket Queue",
    "nav.workspace": "Triage Workspace",
    "nav.audit": "Audit History",
    "nav.runtime": "Runtime Status",
    "nav.aria": "Main navigation",
    "language.label": "Language",
    "session.mode": "Mode",
    "session.ticket": "Ticket",
    "session.logout": "Logout",
    "login.eyebrow": "Local-first staff access",
    "login.supporting": "Secure local workspace for banking ticket triage, policy evidence, draft review, and approval control.",
    "login.mockRole": "Mock role",
    "login.employeeId": "Employee ID",
    "login.fullName": "Full name",
    "login.accessCode": "Access code",
    "login.submit": "Enter workspace",
    "login.submitting": "Checking local session...",
    "login.required": "Employee ID, full name, and access code are required.",
    "login.failed": "Login failed.",
    "queue.eyebrow": "Queue",
    "queue.refresh": "Refresh queue",
    "queue.clear": "Clear mock queue",
    "queue.readonly": "Auditor role is read-only and cannot create tickets.",
    "queue.newTicket": "New customer ticket",
    "queue.create": "Create ticket",
    "queue.loading": "Loading local queue...",
    "queue.emptyTitle": "No tickets in queue",
    "queue.emptyBody": "Create a ticket to start local triage, or switch to real mode after starting the backend stack.",
    "queue.listAria": "Tickets",
    "queue.open": "Open ticket",
    "queue.created": "Created",
    "queue.source": "Source",
    "queue.intent": "Intent",
    "queue.loadError": "Could not load tickets.",
    "queue.createError": "Could not create ticket.",
    "workspace.eyebrow": "Workspace",
    "workspace.title": "Triage Detail Workspace",
    "workspace.reload": "Reload",
    "workspace.readonly": "Read-only",
    "workspace.run": "Analyze and draft",
    "workspace.running": "Running local pipeline...",
    "workspace.noTicketTitle": "No ticket selected",
    "workspace.noTicketBody": "Open a ticket from the queue to begin triage.",
    "workspace.loadTicketError": "Could not load ticket.",
    "workspace.pipelineError": "Pipeline failed.",
    "workspace.reviewError": "Review action failed.",
    "workspace.reviewRecorded": "recorded. Status",
    "workspace.customerTicket": "Customer ticket",
    "workspace.status": "Status",
    "workspace.ticket": "Ticket",
    "workspace.intentUrgency": "Intent and urgency",
    "workspace.confidence": "Confidence",
    "workspace.sentiment": "Sentiment",
    "workspace.policyEvidence": "Policy evidence",
    "workspace.noPolicyTitle": "No policy match",
    "workspace.noPolicyBody": "Manual review is required because no reliable policy context was retrieved.",
    "workspace.policyEmpty": "Run analysis to retrieve policy evidence.",
    "workspace.loadingTicket": "Loading ticket...",
    "draft.empty": "Generate a draft after analysis to review customer-facing language.",
    "draft.aria": "Draft review",
    "draft.title": "Human-reviewed draft",
    "draft.supervisorRequired": "Supervisor approval required before this draft can be approved.",
    "draft.validationFailed": "Draft safety validation failed. Approval is blocked until manual review resolves the issues.",
    "draft.editor": "Draft editor",
    "draft.missingInfo": "Missing info",
    "draft.nextActions": "Next actions",
    "draft.citations": "Policy citations",
    "draft.safetyIssues": "Safety issues",
    "draft.approve": "Approve reviewed draft",
    "draft.requestSupervisor": "Request Supervisor Approval",
    "draft.reject": "Reject draft",
    "draft.auditorReadonly": "Auditor role is read-only.",
    "draft.approvalBlocked": "This role cannot approve this risk level or the draft is not validation-safe.",
    "policy.score": "score",
    "policy.defaultTitle": "Policy evidence",
    "policy.doNot": "Do not do",
    "pipeline.aria": "Pipeline progress",
    "pipeline.done": "Done",
    "pipeline.running": "Running",
    "pipeline.waiting": "Waiting",
    "pipeline.classify": "Classifying intent...",
    "pipeline.urgency": "Scoring urgency...",
    "pipeline.policies": "Retrieving policies...",
    "pipeline.draft": "Drafting response locally...",
    "pipeline.safety": "Validating draft safety...",
    "pipeline.save": "Saving workflow state...",
    "audit.eyebrow": "Review",
    "audit.title": "Audit / Review History",
    "audit.loadError": "Could not load audit history.",
    "audit.noTicketTitle": "No ticket selected",
    "audit.noTicketBody": "Open a ticket before reviewing audit history.",
    "audit.emptyTitle": "No audit entries",
    "audit.emptyBody": "This ticket has no visible audit entries yet.",
    "runtime.eyebrow": "Local runtime",
    "runtime.title": "Runtime Status",
    "runtime.check": "Check again",
    "runtime.loadError": "Could not check runtime status.",
    "runtime.realMode": "Real mode startup",
    "error.recovery": "Check the local runtime status, then retry.",
    "status.DRAFT_READY": "DRAFT READY",
    "status.PENDING_SUPERVISOR": "PENDING SUPERVISOR",
    "status.SUPERVISOR_REQUESTED": "SUPERVISOR REQUESTED",
    "status.APPROVED": "APPROVED",
    "status.NEEDS_INFO": "NEEDS INFO",
    "status.FAILED": "FAILED",
    "status.NEW": "NEW",
    "status.ANALYZED": "ANALYZED",
    "status.REJECTED": "REJECTED",
    "urgency.LOW": "LOW - routine",
    "urgency.MEDIUM": "MEDIUM - monitor",
    "urgency.HIGH": "HIGH - supervisor review",
    "urgency.CRITICAL": "CRITICAL - supervisor required",
    "role.CS_AGENT": "CS_AGENT",
    "role.SUPERVISOR": "SUPERVISOR",
    "role.AUDITOR": "AUDITOR",
    "role.ADMIN": "ADMIN"
  }
} as const;

type LocaleDictionary = typeof translations.vi;
export type TranslationKey = keyof LocaleDictionary;

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    if (typeof window === "undefined") return "vi";
    return window.localStorage.getItem(storageKey) === "en" ? "en" : "vi";
  });

  const value = useMemo<I18nContextValue>(
    () => ({
      language,
      setLanguage(nextLanguage) {
        setLanguageState(nextLanguage);
        window.localStorage.setItem(storageKey, nextLanguage);
      },
      t(key) {
        return translations[language][key] ?? translations.vi[key] ?? key;
      }
    }),
    [language]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function useI18n(): I18nContextValue {
  const value = useContext(I18nContext);
  if (!value) throw new Error("useI18n must be used inside I18nProvider");
  return value;
}

export function statusLabel(status: string, t: (key: TranslationKey) => string): string {
  const key = `status.${status}` as TranslationKey;
  return key in translations.vi ? t(key) : status.replaceAll("_", " ");
}

export function urgencyLabel(level: UrgencyLevel, t: (key: TranslationKey) => string): string {
  return t(`urgency.${level}` as TranslationKey);
}

export function roleLabel(role: Role, t: (key: TranslationKey) => string): string {
  return t(`role.${role}` as TranslationKey);
}
