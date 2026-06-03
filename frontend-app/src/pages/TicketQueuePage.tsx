import { FormEvent, useEffect, useState } from "react";
import type { Ticket } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";
import { RoleGuard } from "../components/RoleGuard";
import { StatusBadge } from "../components/StatusBadge";
import { UrgencyBadge } from "../components/UrgencyBadge";
import { useI18n } from "../i18n";

export function TicketQueuePage({ onOpenTicket }: { onOpenTicket: (ticketId: string) => void }) {
  const { api, employee } = useAuth();
  const { t } = useI18n();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [text, setText] = useState("Khách báo đã lộ OTP và thấy giao dịch 25 triệu không phải do mình thực hiện.");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setTickets(await api.listTickets());
    } catch (err) {
      setError(err instanceof Error ? err : new Error(t("queue.loadError")));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      const ticket = await api.createTicket({ ticket_id: `TICKET-${Date.now()}`, customer_text: text });
      setTickets((items) => [ticket, ...items]);
      onOpenTicket(ticket.ticket_id);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(t("queue.createError")));
    }
  }

  if (!employee) return null;

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">{t("queue.eyebrow")}</p>
          <h1>{t("nav.queue")}</h1>
        </div>
        <button onClick={load}>{t("queue.refresh")}</button>
        {api.mode === "mock" && (
          <button
            onClick={() => {
              api.clearMockTickets?.();
              void load();
            }}
          >
            {t("queue.clear")}
          </button>
        )}
      </header>
      {error && <ErrorBanner error={error} />}
      <RoleGuard role={employee.role} allowed={["CS_AGENT", "SUPERVISOR", "ADMIN"]} fallback={<p className="restriction-note">{t("queue.readonly")}</p>}>
        <form className="create-ticket" onSubmit={create}>
          <label>
            {t("queue.newTicket")}
            <textarea value={text} onChange={(event) => setText(event.target.value)} />
          </label>
          <button className="primary" type="submit">{t("queue.create")}</button>
        </form>
      </RoleGuard>
      {loading && <div className="empty-state">{t("queue.loading")}</div>}
      {!loading && tickets.length === 0 && <EmptyState title={t("queue.emptyTitle")} body={t("queue.emptyBody")} />}
      <section className="ticket-list" aria-label={t("queue.listAria")}>
        {tickets.map((ticket) => (
          <article key={ticket.ticket_id} className="ticket-row">
            <div>
              <strong>{ticket.ticket_id}</strong>
              {ticket.display_title && <h2>{ticket.display_title}</h2>}
              <p>{ticket.customer_text}</p>
              <div className="ticket-meta">
                {ticket.intent && <span>{t("queue.intent")}: {ticket.intent}</span>}
                {ticket.source && <span>{t("queue.source")}: {ticket.source}</span>}
                {ticket.created_at && <span>{t("queue.created")}: {ticket.created_at}</span>}
              </div>
            </div>
            <div className="ticket-badges">
              {ticket.urgency_level && <UrgencyBadge level={ticket.urgency_level} score={ticket.urgency_score} />}
              <StatusBadge status={ticket.status} />
            </div>
            <button onClick={() => onOpenTicket(ticket.ticket_id)}>{t("queue.open")}</button>
          </article>
        ))}
      </section>
    </main>
  );
}
