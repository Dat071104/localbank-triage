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

export function TriageWorkspacePage({ ticketId, onTicketChange }: { ticketId: string | null; onTicketChange: (ticketId: string) => void }) {
  const { api, employee } = useAuth();
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
    void api.getTicket(ticketId).then(setTicket).catch((err) => setError(err instanceof Error ? err : new Error("Could not load ticket.")));
    void api.getAnalysis(ticketId).then(setAnalysis).catch(() => undefined);
    void api.getDraft(ticketId).then((response) => setDraft(normalizeDraft(response))).catch(() => undefined);
  }, [ticketId]);

  if (!employee) return null;
  if (!ticketId) return <EmptyState title="No ticket selected" body="Open a ticket from the queue to begin triage." />;

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
      setError(err instanceof Error ? err : new Error("Pipeline failed."));
    } finally {
      setRunning(false);
    }
  }

  async function review(action: string, editedDraft?: string) {
    if (!ticketId) return;
    setError(null);
    try {
      const result = await api.reviewTicket(ticketId, { action, edited_draft_response: editedDraft });
      setReviewMessage(`${result.action} recorded. Status: ${result.status}`);
      setTicket((current) => (current ? { ...current, status: result.status } : current));
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Review action failed."));
    }
  }

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Workspace</p>
          <h1>Triage Detail Workspace</h1>
        </div>
        <div className="header-actions">
          <button onClick={() => onTicketChange(ticketId)}>Reload</button>
          <RoleGuard role={employee.role} allowed={["CS_AGENT", "SUPERVISOR", "ADMIN"]} fallback={<span className="restriction-note">Read-only</span>}>
            <button className="primary" disabled={running} onClick={runPipeline}>
              {running ? "Running local pipeline..." : "Analyze and draft"}
            </button>
          </RoleGuard>
        </div>
      </header>
      {error && <ErrorBanner error={error} />}
      {reviewMessage && <div className="success-banner">{reviewMessage}</div>}
      <PipelineProgress activeStep={activeStep} running={running} />
      <section className="triage-grid">
        <aside className="triage-column">
          <h2>Customer ticket</h2>
          {ticket ? (
            <>
              <div className="kv"><span>Ticket</span><strong>{ticket.ticket_id}</strong></div>
              <div className="kv"><span>Status</span><StatusBadge status={ticket.status} /></div>
              <p className="customer-text">{ticket.customer_text}</p>
            </>
          ) : (
            <div className="empty-state">Loading ticket...</div>
          )}
          {analysis && (
            <div className="analysis-block">
              <h2>Intent and urgency</h2>
              <div className="kv"><span>Intent</span><strong>{analysis.classification.intent}</strong></div>
              <div className="kv"><span>Confidence</span><strong>{Math.round(analysis.classification.intent_confidence * 100)}%</strong></div>
              <div className="kv"><span>Sentiment</span><strong>{analysis.classification.sentiment}</strong></div>
              <UrgencyBadge level={analysis.urgency.urgency_level} score={analysis.urgency.urgency_score} />
              <ul>{analysis.urgency.reason_codes.map((code) => <li key={code}>{code}</li>)}</ul>
            </div>
          )}
        </aside>
        <section className="triage-column evidence-column">
          <h2>Policy evidence</h2>
          {analysis && analysis.evidence.length === 0 && <EmptyState title="No policy match" body="Manual review is required because no reliable policy context was retrieved." />}
          {analysis ? analysis.evidence.map((item) => <PolicyEvidenceCard key={item.chunk_id} evidence={item} />) : <div className="empty-state">Run analysis to retrieve policy evidence.</div>}
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
