import { FormEvent, useEffect, useState } from "react";
import type { Ticket } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";
import { StatusBadge } from "../components/StatusBadge";
import { RoleGuard } from "../components/RoleGuard";

export function TicketQueuePage({ onOpenTicket }: { onOpenTicket: (ticketId: string) => void }) {
  const { api, employee } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [text, setText] = useState("Khach bao da lo OTP va thay giao dich 25 trieu khong phai do minh thuc hien.");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setTickets(await api.listTickets());
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Could not load tickets."));
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
      setError(err instanceof Error ? err : new Error("Could not create ticket."));
    }
  }

  if (!employee) return null;

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Queue</p>
          <h1>Ticket Queue</h1>
        </div>
        <button onClick={load}>Refresh queue</button>
        {api.mode === "mock" && (
          <button
            onClick={() => {
              api.clearMockTickets?.();
              void load();
            }}
          >
            Clear mock queue
          </button>
        )}
      </header>
      {error && <ErrorBanner error={error} />}
      <RoleGuard role={employee.role} allowed={["CS_AGENT", "SUPERVISOR", "ADMIN"]} fallback={<p className="restriction-note">Auditor role is read-only and cannot create tickets.</p>}>
        <form className="create-ticket" onSubmit={create}>
          <label>
            New customer ticket
            <textarea value={text} onChange={(event) => setText(event.target.value)} />
          </label>
          <button className="primary" type="submit">Create ticket</button>
        </form>
      </RoleGuard>
      {loading && <div className="empty-state">Loading local queue...</div>}
      {!loading && tickets.length === 0 && <EmptyState title="No tickets in queue" body="Create a ticket to start local triage, or switch to real mode after starting the backend stack." />}
      <section className="ticket-list" aria-label="Tickets">
        {tickets.map((ticket) => (
          <article key={ticket.ticket_id} className="ticket-row">
            <div>
              <strong>{ticket.ticket_id}</strong>
              <p>{ticket.customer_text}</p>
            </div>
            <StatusBadge status={ticket.status} />
            <button onClick={() => onOpenTicket(ticket.ticket_id)}>Open ticket</button>
          </article>
        ))}
      </section>
    </main>
  );
}
