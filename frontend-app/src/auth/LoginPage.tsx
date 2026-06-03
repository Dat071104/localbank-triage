import { FormEvent, useState } from "react";
import type { Role } from "../api/types";
import { useAuth } from "./AuthContext";
import { ErrorBanner } from "../components/ErrorBanner";

const roleDefaults: Record<Role, { employee_id: string; full_name: string; access_code: string }> = {
  CS_AGENT: { employee_id: "LBT-CS-0001", full_name: "Nguyễn Hà Trâm", access_code: "LOCAL_ONLY_CHANGE_ME_CS_AGENT" },
  SUPERVISOR: { employee_id: "LBT-SUP-0001", full_name: "Lê Minh Quân", access_code: "LOCAL_ONLY_CHANGE_ME_SUPERVISOR" },
  AUDITOR: { employee_id: "LBT-AUD-0001", full_name: "Phạm Thu Linh", access_code: "LOCAL_ONLY_CHANGE_ME_AUDITOR" },
  ADMIN: { employee_id: "LBT-ADM-0001", full_name: "Đỗ Minh Anh", access_code: "LOCAL_ONLY_CHANGE_ME_ADMIN" }
};

export function LoginPage() {
  const { login, api } = useAuth();
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
      setError(new Error("Employee ID, full name, and access code are required."));
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
      setError(err instanceof Error ? err : new Error("Login failed."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <p className="eyebrow">Local-first staff access</p>
        <h1 id="login-title">LocalBank Triage</h1>
        <p className="supporting">Secure local workspace for banking ticket triage, policy evidence, draft review, and approval control.</p>
        <form onSubmit={submit} className="login-form">
          {api.mode === "mock" && (
            <fieldset className="role-picker">
              <legend>Mock role</legend>
              {(["CS_AGENT", "SUPERVISOR", "AUDITOR", "ADMIN"] as Role[]).map((item) => (
                <button key={item} type="button" className={role === item ? "selected" : ""} onClick={() => chooseRole(item)}>
                  {item.replace("_", " ")}
                </button>
              ))}
            </fieldset>
          )}
          <label>
            Employee ID
            <input value={employeeId} onChange={(event) => setEmployeeId(event.target.value)} autoComplete="username" />
          </label>
          <label>
            Full name
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} autoComplete="name" />
          </label>
          <label>
            Access code
            <input value={accessCode} onChange={(event) => setAccessCode(event.target.value)} type="password" autoComplete="current-password" />
          </label>
          <button className="primary" disabled={submitting} type="submit">
            {submitting ? "Checking local session..." : "Enter workspace"}
          </button>
        </form>
        {error && <ErrorBanner error={error} />}
      </section>
    </main>
  );
}
