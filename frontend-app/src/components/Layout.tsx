import { useAuth } from "../auth/AuthContext";
import { roleLabel, useI18n } from "../i18n";

export type PageKey = "queue" | "workspace" | "audit" | "runtime";

const labelKeys: Record<PageKey, "nav.queue" | "nav.workspace" | "nav.audit" | "nav.runtime"> = {
  queue: "nav.queue",
  workspace: "nav.workspace",
  audit: "nav.audit",
  runtime: "nav.runtime"
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
  const { language, setLanguage, t } = useI18n();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">LocalBank</p>
          <h1>Triage</h1>
        </div>
        <div className="language-toggle" aria-label={t("language.label")}>
          <button type="button" className={language === "vi" ? "active" : ""} onClick={() => setLanguage("vi")}>VI</button>
          <button type="button" className={language === "en" ? "active" : ""} onClick={() => setLanguage("en")}>EN</button>
        </div>
        <nav aria-label={t("nav.aria")}>
          {(Object.keys(labelKeys) as PageKey[]).map((item) => (
            <button key={item} className={page === item ? "active" : ""} onClick={() => onPageChange(item)}>
              {t(labelKeys[item])}
            </button>
          ))}
        </nav>
        <div className="session-card">
          <strong>{employee?.display_name}</strong>
          {employee && <span>{roleLabel(employee.role, t)}</span>}
          <span>{t("session.mode")}: {api.mode}</span>
          {selectedTicketId && <span>{t("session.ticket")}: {selectedTicketId}</span>}
          <button type="button" onClick={logout}>{t("session.logout")}</button>
        </div>
      </aside>
      <section className="content-shell">{children}</section>
    </div>
  );
}
