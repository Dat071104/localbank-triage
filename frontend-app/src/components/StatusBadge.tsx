import { statusLabel, useI18n } from "../i18n";

export function StatusBadge({ status }: { status: string }) {
  const { t } = useI18n();
  return <span className="badge neutral">{statusLabel(status, t)}</span>;
}
