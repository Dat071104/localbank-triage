import { useEffect, useState } from "react";
import type { Draft, Role } from "../api/types";
import { UrgencyBadge } from "./UrgencyBadge";

function canApprove(role: Role, level: Draft["risk_level"]) {
  if (role === "ADMIN" || role === "SUPERVISOR") return true;
  if (role === "CS_AGENT") return level === "LOW" || level === "MEDIUM";
  return false;
}

export function DraftReviewPanel({
  draft,
  role,
  onApprove,
  onReject,
  onRequestSupervisor,
  readonly = false
}: {
  draft: Draft | null;
  role: Role;
  onApprove: (editedDraft: string) => Promise<void>;
  onReject: () => Promise<void>;
  onRequestSupervisor: () => Promise<void>;
  readonly?: boolean;
}) {
  const [edited, setEdited] = useState(draft?.draft_response ?? "");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setEdited(draft?.draft_response ?? "");
  }, [draft?.draft_response]);

  if (!draft) {
    return <div className="empty-state">Generate a draft after analysis to review customer-facing language.</div>;
  }

  const approvalAllowed = canApprove(role, draft.risk_level) && !readonly && draft.validation_passed !== false;
  const requiresSupervisor = draft.risk_level === "HIGH" || draft.risk_level === "CRITICAL" || draft.requires_supervisor_approval;

  async function run(action: () => Promise<void>) {
    setBusy(true);
    try {
      await action();
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="draft-panel" aria-label="Draft review">
      <div className="panel-heading">
        <h2>Human-reviewed draft</h2>
        <UrgencyBadge level={draft.risk_level} />
      </div>
      {requiresSupervisor && <div className="supervisor-alert">Supervisor approval required before this draft can be approved.</div>}
      {draft.validation_passed === false && (
        <div className="supervisor-alert">Draft safety validation failed. Approval is blocked until manual review resolves the issues.</div>
      )}
      <label>
        Draft editor
        <textarea value={edited} onChange={(event) => setEdited(event.target.value)} readOnly={readonly} aria-label="Draft editor" />
      </label>
      <div className="review-lists">
        <div>
          <h3>Missing info</h3>
          <ul>{draft.missing_info.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
        <div>
          <h3>Next actions</h3>
          <ul>{draft.next_actions.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      </div>
      <div>
        <h3>Policy citations</h3>
        <ul>{draft.policy_citations.map((item) => <li key={`${item.policy_id}-${item.chunk_id}`}>{item.policy_id} / {item.chunk_id}</li>)}</ul>
      </div>
      {draft.validation_issues && draft.validation_issues.length > 0 && (
        <div>
          <h3>Safety issues</h3>
          <ul>{draft.validation_issues.map((item) => <li key={item.code}>{item.code}: {item.message}</li>)}</ul>
        </div>
      )}
      <div className="actions">
        <button className="primary" disabled={!approvalAllowed || busy} onClick={() => run(() => onApprove(edited))}>
          Approve reviewed draft
        </button>
        {requiresSupervisor && role === "CS_AGENT" && (
          <button disabled={readonly || busy} onClick={() => run(onRequestSupervisor)}>
            Request Supervisor Approval
          </button>
        )}
        <button disabled={readonly || busy || role === "AUDITOR"} onClick={() => run(onReject)}>
          Reject draft
        </button>
      </div>
      {!approvalAllowed && (
        <p className="restriction-note">
          {role === "AUDITOR" ? "Auditor role is read-only." : "This role cannot approve this risk level or the draft is not validation-safe."}
        </p>
      )}
    </section>
  );
}
