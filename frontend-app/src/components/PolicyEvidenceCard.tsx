import type { PolicyEvidence } from "../api/types";

export function PolicyEvidenceCard({ evidence }: { evidence: PolicyEvidence }) {
  const restricted = evidence.section.toLowerCase().includes("khong") || evidence.text.includes("Không được làm");
  return (
    <article className={`evidence-card ${restricted ? "restricted" : ""}`}>
      <div className="evidence-meta">
        <strong>{evidence.policy_id}</strong>
        <span>{evidence.chunk_id}</span>
        <span>{evidence.section}</span>
        <span>score {evidence.score.toFixed(2)}</span>
      </div>
      <h3>{evidence.title ?? "Policy evidence"}</h3>
      {restricted && <p className="do-not">Không được làm</p>}
      <p>{evidence.text}</p>
    </article>
  );
}
