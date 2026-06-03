import { useEffect, useState } from "react";
import type { AuditLog } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";
import { statusLabel, useI18n } from "../i18n";

export function AuditPage({ ticketId }: { ticketId: string | null }) {
  const { api } = useAuth();
  const { t } = useI18n();
  const [items, setItems] = useState<AuditLog[]>([]);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!ticketId) return;
    setError(null);
    api.getAudit(ticketId).then(setItems).catch((err) => setError(err instanceof Error ? err : new Error(t("audit.loadError"))));
  }, [api, ticketId, t]);

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">{t("audit.eyebrow")}</p>
          <h1>{t("audit.title")}</h1>
        </div>
      </header>
      {error && <ErrorBanner error={error} />}
      {!ticketId && <EmptyState title={t("audit.noTicketTitle")} body={t("audit.noTicketBody")} />}
      {ticketId && items.length === 0 && !error && <EmptyState title={t("audit.emptyTitle")} body={t("audit.emptyBody")} />}
      <section className="audit-list">
        {items.map((item, index) => (
          <article key={`${item.action}-${index}`} className="audit-row">
            <strong>{item.action}</strong>
            <span>{statusLabel(item.status.toUpperCase(), t)}</span>
            <span>{item.actor_role} / {item.actor_employee_id}</span>
          </article>
        ))}
      </section>
    </main>
  );
}
