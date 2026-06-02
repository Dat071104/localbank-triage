import { useEffect, useState } from "react";
import type { AuditLog } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";

export function AuditPage({ ticketId }: { ticketId: string | null }) {
  const { api } = useAuth();
  const [items, setItems] = useState<AuditLog[]>([]);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!ticketId) return;
    setError(null);
    api.getAudit(ticketId).then(setItems).catch((err) => setError(err instanceof Error ? err : new Error("Could not load audit history.")));
  }, [api, ticketId]);

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Review</p>
          <h1>Audit / Review History</h1>
        </div>
      </header>
      {error && <ErrorBanner error={error} />}
      {!ticketId && <EmptyState title="No ticket selected" body="Open a ticket before reviewing audit history." />}
      {ticketId && items.length === 0 && !error && <EmptyState title="No audit entries" body="This ticket has no visible audit entries yet." />}
      <section className="audit-list">
        {items.map((item, index) => (
          <article key={`${item.action}-${index}`} className="audit-row">
            <strong>{item.action}</strong>
            <span>{item.status}</span>
            <span>{item.actor_role} / {item.actor_employee_id}</span>
          </article>
        ))}
      </section>
    </main>
  );
}
