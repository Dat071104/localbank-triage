import { FormEvent, useState } from "react";
import type { Role } from "../api/types";
import { useAuth } from "./AuthContext";
import { ErrorBanner } from "../components/ErrorBanner";
import { roleLabel, useI18n } from "../i18n";

const roleDefaults: Record<Role, { employee_id: string; full_name: string; access_code: string }> = {
  CS_AGENT: { employee_id: "LBT-CS-0001", full_name: "Nguyen Ha Tram", access_code: "LOCAL_ONLY_CHANGE_ME_CS_AGENT" },
  SUPERVISOR: { employee_id: "LBT-SUP-0001", full_name: "Le Minh Quan", access_code: "LOCAL_ONLY_CHANGE_ME_SUPERVISOR" },
  AUDITOR: { employee_id: "LBT-AUD-0001", full_name: "Pham Thu Linh", access_code: "LOCAL_ONLY_CHANGE_ME_AUDITOR" },
  ADMIN: { employee_id: "LBT-ADM-0001", full_name: "Do Minh Anh", access_code: "LOCAL_ONLY_CHANGE_ME_ADMIN" }
};

export function LoginPage() {
  const { login, api } = useAuth();
  const { t } = useI18n();
  const [role, setRole] = useState<Role>("CS_AGENT");
  const [employeeId, setEmployeeId] = useState(roleDefaults.CS_AGENT.employee_id);
  const [fullName, setFullName] = useState(roleDefaults.CS_AGENT.full_name);
  const [accessCode, setAccessCode] = useState(roleDefaults.CS_AGENT.access_code);
  const [error, setError] = useState<Error | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function chooseRole(nextRole: Role) {
    setRole(nextRole);
    setEmployeeId(roleDefaults[nextRole].employee_id);
    setFullName(roleDefaults[nextRole].full_name);
    setAccessCode(roleDefaults[nextRole].access_code);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (!employeeId.trim() || !fullName.trim() || !accessCode.trim()) {
      setError(new Error(t("login.required")));
      return;
    }
    setSubmitting(true);
    try {
      await login({
        employee_id: employeeId.trim(),
        full_name: fullName.trim(),
        access_code: accessCode,
        device_id: "localbank-web",
        mock_role: role
      });
    } catch (err) {
      setError(err instanceof Error ? err : new Error(t("login.failed")));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <p className="eyebrow">{t("login.eyebrow")}</p>
        <h1 id="login-title">{t("app.product")}</h1>
        <p className="supporting">{t("login.supporting")}</p>
        <form onSubmit={submit} className="login-form">
          {api.mode === "mock" && (
            <fieldset className="role-picker">
              <legend>{t("login.mockRole")}</legend>
              {(["CS_AGENT", "SUPERVISOR", "AUDITOR", "ADMIN"] as Role[]).map((item) => (
                <button key={item} type="button" className={role === item ? "selected" : ""} onClick={() => chooseRole(item)}>
                  {roleLabel(item, t).replace("_", " ")}
                </button>
              ))}
            </fieldset>
          )}
          <label>
            {t("login.employeeId")}
            <input value={employeeId} onChange={(event) => setEmployeeId(event.target.value)} autoComplete="username" />
          </label>
          <label>
            {t("login.fullName")}
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} autoComplete="name" />
          </label>
          <label>
            {t("login.accessCode")}
            <input value={accessCode} onChange={(event) => setAccessCode(event.target.value)} type="password" autoComplete="current-password" />
          </label>
          <button className="primary" disabled={submitting} type="submit">
            {submitting ? t("login.submitting") : t("login.submit")}
          </button>
        </form>
        {error && <ErrorBanner error={error} />}
      </section>
    </main>
  );
}
