import { useEffect, useState } from "react";
import type { Analysis, Draft, DraftResponse, Ticket } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { DraftReviewPanel } from "../components/DraftReviewPanel";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";
import { PipelineProgress } from "../components/PipelineProgress";
import { PolicyEvidenceCard } from "../components/PolicyEvidenceCard";
import { RoleGuard } from "../components/RoleGuard";
import { StatusBadge } from "../components/StatusBadge";
import { UrgencyBadge } from "../components/UrgencyBadge";
import { statusLabel, useI18n } from "../i18n";

export function TriageWorkspacePage({ ticketId, onTicketChange }: { ticketId: string | null; onTicketChange: (ticketId: string) => void }) {
  const { api, employee } = useAuth();
  const { t } = useI18n();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [running, setRunning] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [reviewMessage, setReviewMessage] = useState("");

  useEffect(() => {
    if (!ticketId) return;
    setError(null);
    void api.getTicket(ticketId).then(setTicket).catch((err) => setError(err instanceof Error ? err : new Error(t("workspace.loadTicketError"))));
    void api.getAnalysis(ticketId).then(setAnalysis).catch(() => undefined);
    void api.getDraft(ticketId).then((response) => setDraft(normalizeDraft(response))).catch(() => undefined);
  }, [api, ticketId, t]);

  if (!employee) return null;
  if (!ticketId) return <EmptyState title={t("workspace.noTicketTitle")} body={t("workspace.noTicketBody")} />;

  async function runPipeline() {
    if (!ticketId) return;
    setRunning(true);
    setError(null);
    setReviewMessage("");
    try {
      setActiveStep(0);
      const analysisResult = await api.analyzeTicket(ticketId);
      setAnalysis(analysisResult);
      setActiveStep(3);
      const draftResult = await api.createDraft(ticketId);
      setDraft(normalizeDraft(draftResult));
      setActiveStep(6);
      const updated = await api.getTicket(ticketId);
      setTicket(updated);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(t("workspace.pipelineError")));
    } finally {
      setRunning(false);
    }
  }

  async function review(action: string, editedDraft?: string) {
    if (!ticketId) return;
    setError(null);
    try {
      const result = await api.reviewTicket(ticketId, { action, edited_draft_response: editedDraft });
      setReviewMessage(`${result.action} ${t("workspace.reviewRecorded")}: ${statusLabel(result.status, t)}`);
      setTicket((current) => (current ? { ...current, status: result.status } : current));
    } catch (err) {
      setError(err instanceof Error ? err : new Error(t("workspace.reviewError")));
    }
  }

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">{t("workspace.eyebrow")}</p>
          <h1>{t("workspace.title")}</h1>
        </div>
        <div className="header-actions">
          <button onClick={() => onTicketChange(ticketId)}>{t("workspace.reload")}</button>
          <RoleGuard role={employee.role} allowed={["CS_AGENT", "SUPERVISOR", "ADMIN"]} fallback={<span className="restriction-note">{t("workspace.readonly")}</span>}>
            <button className="primary" disabled={running} onClick={runPipeline}>
              {running ? t("workspace.running") : t("workspace.run")}
            </button>
          </RoleGuard>
        </div>
      </header>
      {error && <ErrorBanner error={error} />}
      {reviewMessage && <div className="success-banner">{reviewMessage}</div>}
      <PipelineProgress activeStep={activeStep} running={running} />
      <section className="triage-grid">
        <aside className="triage-column">
          <h2>{t("workspace.customerTicket")}</h2>
          {ticket ? (
            <>
              <div className="kv"><span>{t("workspace.ticket")}</span><strong>{ticket.ticket_id}</strong></div>
              <div className="kv"><span>{t("workspace.status")}</span><StatusBadge status={ticket.status} /></div>
              {ticket.display_title && <h3>{ticket.display_title}</h3>}
              <p className="customer-text">{ticket.customer_text}</p>
            </>
          ) : (
            <div className="empty-state">{t("workspace.loadingTicket")}</div>
          )}
          {analysis && (
            <div className="analysis-block">
              <h2>{t("workspace.intentUrgency")}</h2>
              <div className="kv"><span>{t("queue.intent")}</span><strong>{analysis.classification.intent}</strong></div>
              <div className="kv"><span>{t("workspace.confidence")}</span><strong>{Math.round(analysis.classification.intent_confidence * 100)}%</strong></div>
              <div className="kv"><span>{t("workspace.sentiment")}</span><strong>{analysis.classification.sentiment}</strong></div>
              <UrgencyBadge level={analysis.urgency.urgency_level} score={analysis.urgency.urgency_score} />
              <ul>{analysis.urgency.reason_codes.map((code) => <li key={code}>{code}</li>)}</ul>
            </div>
          )}
        </aside>
        <section className="triage-column evidence-column">
          <h2>{t("workspace.policyEvidence")}</h2>
          {analysis && analysis.evidence.length === 0 && <EmptyState title={t("workspace.noPolicyTitle")} body={t("workspace.noPolicyBody")} />}
          {analysis ? analysis.evidence.map((item) => <PolicyEvidenceCard key={item.chunk_id} evidence={item} />) : <div className="empty-state">{t("workspace.policyEmpty")}</div>}
        </section>
        <aside className="triage-column">
          <DraftReviewPanel
            draft={draft}
            role={employee.role}
            readonly={employee.role === "AUDITOR"}
            onApprove={(editedDraft) => review("APPROVE", editedDraft)}
            onReject={() => review("REJECT")}
            onRequestSupervisor={() => review("REQUEST_SUPERVISOR")}
          />
        </aside>
      </section>
    </main>
  );
}

function normalizeDraft(response: DraftResponse): Draft {
  return "draft" in response.draft ? { ...response.draft.draft, validation_passed: response.draft.validation_passed, validation_issues: response.draft.validation_issues, used_fallback: response.draft.used_fallback } : response.draft;
}
