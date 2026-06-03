import { useState } from "react";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { LoginPage } from "./auth/LoginPage";
import { Layout, PageKey } from "./components/Layout";
import { TicketQueuePage } from "./pages/TicketQueuePage";
import { TriageWorkspacePage } from "./pages/TriageWorkspacePage";
import { AuditPage } from "./pages/AuditPage";
import { RuntimeStatusPage } from "./pages/RuntimeStatusPage";
import { I18nProvider } from "./i18n";

function Workspace() {
  const { employee } = useAuth();
  const [page, setPage] = useState<PageKey>("queue");
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>("OTP-CRITICAL-001");

  if (!employee) return <LoginPage />;

  return (
    <Layout page={page} onPageChange={setPage} selectedTicketId={selectedTicketId}>
      {page === "queue" && <TicketQueuePage onOpenTicket={(ticketId) => { setSelectedTicketId(ticketId); setPage("workspace"); }} />}
      {page === "workspace" && <TriageWorkspacePage ticketId={selectedTicketId} onTicketChange={setSelectedTicketId} />}
      {page === "audit" && <AuditPage ticketId={selectedTicketId} />}
      {page === "runtime" && <RuntimeStatusPage />}
    </Layout>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <AuthProvider>
        <Workspace />
      </AuthProvider>
    </I18nProvider>
  );
}
