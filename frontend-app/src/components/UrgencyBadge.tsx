import type { UrgencyLevel } from "../api/types";

const labels: Record<UrgencyLevel, string> = {
  LOW: "LOW - routine",
  MEDIUM: "MEDIUM - monitor",
  HIGH: "HIGH - supervisor review",
  CRITICAL: "CRITICAL - supervisor required"
};

export function UrgencyBadge({ level, score }: { level: UrgencyLevel; score?: number }) {
  return (
    <span className={`badge urgency ${level.toLowerCase()}`} aria-label={`Urgency ${labels[level]}`}>
      {labels[level]}{typeof score === "number" ? ` (${score})` : ""}
    </span>
  );
}
