import type { PolicyEvidence } from "../api/types";
import { useI18n } from "../i18n";

export function PolicyEvidenceCard({ evidence }: { evidence: PolicyEvidence }) {
  const { t } = useI18n();
  const restricted = evidence.section.toLowerCase().includes("khong") || evidence.section.toLowerCase().includes("không") || evidence.text.toLowerCase().includes("không hỏi");
  return (
    <article className={`evidence-card ${restricted ? "restricted" : ""}`}>
      <div className="evidence-meta">
        <strong>{evidence.policy_id}</strong>
        <span>{evidence.chunk_id}</span>
        <span>{evidence.section}</span>
        <span>{t("policy.score")} {evidence.score.toFixed(2)}</span>
      </div>
      <h3>{evidence.title ?? t("policy.defaultTitle")}</h3>
      {restricted && <p className="do-not">{t("policy.doNot")}</p>}
      <p>{evidence.text}</p>
    </article>
  );
}
