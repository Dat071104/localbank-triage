import { useEffect, useState } from "react";
import type { RuntimeStatus } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { ErrorBanner } from "../components/ErrorBanner";
import { useI18n } from "../i18n";

export function RuntimeStatusPage() {
  const { api } = useAuth();
  const { t } = useI18n();
  const [items, setItems] = useState<RuntimeStatus[]>([]);
  const [error, setError] = useState<Error | null>(null);

  async function load() {
    setError(null);
    try {
      setItems(await api.getRuntimeStatus());
    } catch (err) {
      setError(err instanceof Error ? err : new Error(t("runtime.loadError")));
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">{t("runtime.eyebrow")}</p>
          <h1>{t("runtime.title")}</h1>
        </div>
        <button onClick={load}>{t("runtime.check")}</button>
      </header>
      {error && <ErrorBanner error={error} />}
      <section className="runtime-grid">
        {items.map((item) => (
          <article key={item.name} className={`runtime-card ${item.status}`}>
            <strong>{item.name}</strong>
            <span>{item.status}</span>
            <p>{item.detail}</p>
          </article>
        ))}
      </section>
      <section className="setup-commands">
        <h2>{t("runtime.realMode")}</h2>
        <pre>{`docker compose up -d postgres redis qdrant
cd "D:\\Project cua Dat\\Localbank-triage"
# mở auth-service, api-gateway, classifier, urgency, rag, llm, worker ở các terminal riêng
cd frontend-app
$env:VITE_API_MODE="real"; npm run dev`}</pre>
      </section>
    </main>
  );
}
