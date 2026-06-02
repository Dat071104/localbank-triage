import { useAuth } from "../auth/AuthContext";

export type PageKey = "queue" | "workspace" | "audit" | "runtime";

const labels: Record<PageKey, string> = {
  queue: "Ticket Queue",
  workspace: "Triage Workspace",
  audit: "Audit History",
  runtime: "Runtime Status"
};

export function Layout({
  page,
  onPageChange,
  selectedTicketId,
  children
}: {
  page: PageKey;
  onPageChange: (page: PageKey) => void;
  selectedTicketId: string | null;
  children: React.ReactNode;
}) {
  const { employee, logout, api } = useAuth();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">LocalBank</p>
          <h1>Triage</h1>
        </div>
        <nav aria-label="Main">
          {(Object.keys(labels) as PageKey[]).map((item) => (
            <button key={item} className={page === item ? "active" : ""} onClick={() => onPageChange(item)}>
              {labels[item]}
            </button>
          ))}
        </nav>
        <div className="session-card">
          <strong>{employee?.display_name}</strong>
          <span>{employee?.role.replace("_", " ")}</span>
          <span>Mode: {api.mode}</span>
          {selectedTicketId && <span>Ticket: {selectedTicketId}</span>}
          <button type="button" onClick={logout}>Logout</button>
        </div>
      </aside>
      <section className="content-shell">{children}</section>
    </div>
  );
}
