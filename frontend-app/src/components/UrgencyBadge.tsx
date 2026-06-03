import type { UrgencyLevel } from "../api/types";
import { urgencyLabel, useI18n } from "../i18n";

export function UrgencyBadge({ level, score }: { level: UrgencyLevel; score?: number }) {
  const { t } = useI18n();
  const label = urgencyLabel(level, t);
  return (
    <span className={`badge urgency ${level.toLowerCase()}`} aria-label={`Urgency ${label}`}>
      {label}{typeof score === "number" ? ` (${score})` : ""}
    </span>
  );
}
