import { useEffect, useState } from "react";
import type { RuntimeStatus } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { ErrorBanner } from "../components/ErrorBanner";

export function RuntimeStatusPage() {
  const { api } = useAuth();
  const [items, setItems] = useState<RuntimeStatus[]>([]);
  const [error, setError] = useState<Error | null>(null);

  async function load() {
    setError(null);
    try {
      setItems(await api.getRuntimeStatus());
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Could not check runtime status."));
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <main className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Local runtime</p>
          <h1>Runtime Status</h1>
        </div>
        <button onClick={load}>Check again</button>
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
        <h2>Real mode startup</h2>
        <pre>{`docker compose up -d postgres redis qdrant
cd "D:\\Project cua Dat\\Localbank-triage"
# start auth-service, api-gateway, classifier, urgency, rag, llm, worker in separate terminals
cd frontend-app
$env:VITE_API_MODE="real"; npm run dev`}</pre>
      </section>
    </main>
  );
}
