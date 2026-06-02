import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { LoginPage } from "../../src/auth/LoginPage";
import { AuthProvider } from "../../src/auth/AuthContext";
import { UrgencyBadge } from "../../src/components/UrgencyBadge";
import { RoleGuard } from "../../src/components/RoleGuard";
import { PolicyEvidenceCard } from "../../src/components/PolicyEvidenceCard";
import { DraftReviewPanel } from "../../src/components/DraftReviewPanel";
import { PipelineProgress } from "../../src/components/PipelineProgress";
import { ErrorBanner } from "../../src/components/ErrorBanner";

describe("login form", () => {
  it("validates required staff fields", async () => {
    render(
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    );
    await userEvent.clear(screen.getByLabelText(/Employee ID/i));
    await userEvent.click(screen.getByRole("button", { name: /Enter workspace/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent("required");
  });
});

describe("core components", () => {
  it("renders urgency labels beyond color alone", () => {
    render(<UrgencyBadge level="CRITICAL" score={96} />);
    expect(screen.getByLabelText(/CRITICAL - supervisor required/i)).toBeInTheDocument();
  });

  it("guards restricted content by role", () => {
    render(<RoleGuard role="AUDITOR" allowed={["ADMIN"]} fallback={<span>blocked</span>}><span>secret</span></RoleGuard>);
    expect(screen.getByText("blocked")).toBeInTheDocument();
    expect(screen.queryByText("secret")).not.toBeInTheDocument();
  });

  it("displays policy identifiers and restricted section", () => {
    render(
      <PolicyEvidenceCard
        evidence={{
          policy_id: "FRAUD-002",
          chunk_id: "FRAUD-002#khong-duoc-lam",
          title: "OTP",
          section: "Không được làm",
          score: 0.94,
          text: "Không được làm: do not request OTP."
        }}
      />
    );
    expect(screen.getByText("FRAUD-002")).toBeInTheDocument();
    expect(screen.getByText("FRAUD-002#khong-duoc-lam")).toBeInTheDocument();
    expect(screen.getAllByText("Không được làm").length).toBeGreaterThan(0);
  });

  it("blocks critical approval for CS_AGENT", () => {
    render(
      <DraftReviewPanel
        role="CS_AGENT"
        draft={{
          summary: "critical fraud",
          risk_level: "CRITICAL",
          draft_response: "Reviewed draft",
          next_actions: ["Escalate"],
          missing_info: ["Timestamp"],
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
    expect(screen.getByRole("button", { name: /Approve reviewed draft/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /Request Supervisor Approval/i })).toBeEnabled();
  });

  it("shows pipeline steps and error recovery text", () => {
    render(<PipelineProgress activeStep={2} running />);
    expect(screen.getByText("Classifying intent...")).toBeInTheDocument();
    expect(screen.getByText("Retrieving policies...")).toBeInTheDocument();
    render(<ErrorBanner error={Object.assign(new Error("Service failed"), { recovery: "Retry after runtime check." })} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Retry after runtime check");
  });
});
