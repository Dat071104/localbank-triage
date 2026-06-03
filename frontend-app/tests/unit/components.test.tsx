import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LoginPage } from "../../src/auth/LoginPage";
import { AuthProvider } from "../../src/auth/AuthContext";
import { DraftReviewPanel } from "../../src/components/DraftReviewPanel";
import { ErrorBanner } from "../../src/components/ErrorBanner";
import { PipelineProgress } from "../../src/components/PipelineProgress";
import { PolicyEvidenceCard } from "../../src/components/PolicyEvidenceCard";
import { RoleGuard } from "../../src/components/RoleGuard";
import { UrgencyBadge } from "../../src/components/UrgencyBadge";
import { I18nProvider, useI18n } from "../../src/i18n";
import { createMockClient } from "../../src/api/mockClient";

function renderWithProviders(ui: React.ReactNode) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

beforeEach(() => {
  window.localStorage.removeItem("localbank_language");
});

describe("login form", () => {
  it("validates required staff fields in Vietnamese by default", async () => {
    renderWithProviders(
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    );
    expect(screen.getByRole("heading", { name: "LocalBank Triage" })).toBeInTheDocument();
    expect(screen.getByText("Truy cập nội bộ local-first")).toBeInTheDocument();
    await userEvent.clear(screen.getByLabelText(/Mã nhân viên/i));
    await userEvent.click(screen.getByRole("button", { name: /Vào không gian xử lý/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Cần nhập mã nhân viên");
  });
});

describe("mock queue data", () => {
  it("renders multiple diverse seeded tickets with expected urgency behavior", async () => {
    const api = createMockClient();
    await api.login({ employee_id: "cs001", full_name: "Mai Tran", access_code: "local", device_id: "unit", mock_role: "CS_AGENT" });
    const tickets = await api.listTickets();
    expect(tickets).toHaveLength(7);
    expect(tickets.map((ticket) => ticket.ticket_id)).toEqual([
      "OTP-CRITICAL-001",
      "CARD-CRITICAL-002",
      "SEC-HIGH-003",
      "APP-MEDIUM-004",
      "FEE-LOW-005",
      "INFO-LOW-006",
      "SAFE-MANUAL-007"
    ]);
    expect(tickets.find((ticket) => ticket.ticket_id === "OTP-CRITICAL-001")?.urgency_level).toBe("CRITICAL");
    expect(tickets.find((ticket) => ticket.ticket_id === "INFO-LOW-006")?.urgency_level).toBe("LOW");
  });
});

describe("core components", () => {
  it("renders Vietnamese urgency labels beyond color alone", () => {
    renderWithProviders(<UrgencyBadge level="CRITICAL" score={96} />);
    expect(screen.getByLabelText(/RẤT KHẨN CẤP - cần supervisor/i)).toBeInTheDocument();
  });

  it("guards restricted content by role", () => {
    render(<RoleGuard role="AUDITOR" allowed={["ADMIN"]} fallback={<span>blocked</span>}><span>secret</span></RoleGuard>);
    expect(screen.getByText("blocked")).toBeInTheDocument();
    expect(screen.queryByText("secret")).not.toBeInTheDocument();
  });

  it("displays policy identifiers and restricted section", () => {
    renderWithProviders(
      <PolicyEvidenceCard
        evidence={{
          policy_id: "FRAUD-002",
          chunk_id: "FRAUD-002#otp-giao-dich",
          title: "OTP",
          section: "Không được làm",
          score: 0.94,
          text: "Không hỏi lại toàn bộ OTP."
        }}
      />
    );
    expect(screen.getByText("FRAUD-002")).toBeInTheDocument();
    expect(screen.getByText("FRAUD-002#otp-giao-dich")).toBeInTheDocument();
    expect(screen.getAllByText("Không được làm").length).toBeGreaterThan(0);
  });

  it("blocks critical approval for CS_AGENT", () => {
    renderWithProviders(
      <DraftReviewPanel
        role="CS_AGENT"
        draft={{
          summary: "critical fraud",
          risk_level: "CRITICAL",
          draft_response: "Reviewed draft",
          next_actions: ["Chuyển supervisor"],
          missing_info: ["Thời điểm giao dịch"],
          policy_citations: [{ policy_id: "FRAUD-002", chunk_id: "1" }],
          auto_send_allowed: false,
          requires_supervisor_approval: true,
          validation_passed: true
        }}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onRequestSupervisor={vi.fn()}
      />
    );
    expect(screen.getByRole("button", { name: /Duyệt bản nháp đã kiểm tra/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /Yêu cầu supervisor duyệt/i })).toBeEnabled();
  });

  it("switches language from Vietnamese to English", async () => {
    function ToggleHarness() {
      const { language, setLanguage, t } = useI18n();
      return (
        <div>
          <p>{t("nav.queue")}</p>
          <button onClick={() => setLanguage(language === "vi" ? "en" : "vi")}>switch</button>
        </div>
      );
    }

    renderWithProviders(<ToggleHarness />);
    expect(screen.getByText("Hàng đợi ticket")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "switch" }));
    expect(screen.getByText("Ticket Queue")).toBeInTheDocument();
  });

  it("shows pipeline steps and error recovery text", () => {
    renderWithProviders(<PipelineProgress activeStep={2} running />);
    expect(screen.getByText("Đang phân loại ý định...")).toBeInTheDocument();
    expect(screen.getByText("Đang truy xuất chính sách...")).toBeInTheDocument();
    renderWithProviders(<ErrorBanner error={Object.assign(new Error("Dịch vụ lỗi"), { recovery: "Thử lại sau khi kiểm tra hệ thống." })} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Thử lại sau khi kiểm tra hệ thống");
  });
});
