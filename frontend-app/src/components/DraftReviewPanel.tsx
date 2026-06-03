import { useEffect, useState } from "react";
import type { Draft, Role } from "../api/types";
import { useI18n } from "../i18n";
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
  const { t } = useI18n();
  const [edited, setEdited] = useState(draft?.draft_response ?? "");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setEdited(draft?.draft_response ?? "");
  }, [draft?.draft_response]);

  if (!draft) {
    return <div className="empty-state">{t("draft.empty")}</div>;
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
    <section className="draft-panel" aria-label={t("draft.aria")}>
      <div className="panel-heading">
        <h2>{t("draft.title")}</h2>
        <UrgencyBadge level={draft.risk_level} />
      </div>
      {requiresSupervisor && <div className="supervisor-alert">{t("draft.supervisorRequired")}</div>}
      {draft.validation_passed === false && <div className="supervisor-alert">{t("draft.validationFailed")}</div>}
      <label>
        {t("draft.editor")}
        <textarea value={edited} onChange={(event) => setEdited(event.target.value)} readOnly={readonly} aria-label={t("draft.editor")} />
      </label>
      <div className="review-lists">
        <div>
          <h3>{t("draft.missingInfo")}</h3>
          <ul>{draft.missing_info.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
        <div>
          <h3>{t("draft.nextActions")}</h3>
          <ul>{draft.next_actions.map((item) => <li key={item}>{item}</li>)}</ul>
        </div>
      </div>
      <div>
        <h3>{t("draft.citations")}</h3>
        <ul>{draft.policy_citations.map((item) => <li key={`${item.policy_id}-${item.chunk_id}`}>{item.policy_id} / {item.chunk_id}</li>)}</ul>
      </div>
      {draft.validation_issues && draft.validation_issues.length > 0 && (
        <div>
          <h3>{t("draft.safetyIssues")}</h3>
          <ul>{draft.validation_issues.map((item) => <li key={item.code}>{item.code}: {item.message}</li>)}</ul>
        </div>
      )}
      <div className="actions">
        <button className="primary" disabled={!approvalAllowed || busy} onClick={() => run(() => onApprove(edited))}>
          {t("draft.approve")}
        </button>
        {requiresSupervisor && role === "CS_AGENT" && (
          <button disabled={readonly || busy} onClick={() => run(onRequestSupervisor)}>
            {t("draft.requestSupervisor")}
          </button>
        )}
        <button disabled={readonly || busy || role === "AUDITOR"} onClick={() => run(onReject)}>
          {t("draft.reject")}
        </button>
      </div>
      {!approvalAllowed && (
        <p className="restriction-note">
          {role === "AUDITOR" ? t("draft.auditorReadonly") : t("draft.approvalBlocked")}
        </p>
      )}
    </section>
  );
}
