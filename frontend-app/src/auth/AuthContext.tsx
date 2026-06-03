import { createContext, useContext, useMemo, useState } from "react";
import { createApiClient } from "../api/client";
import type { AppApi, Employee, LoginRequest } from "../api/types";

interface AuthContextValue {
  api: AppApi;
  employee: Employee | null;
  login(payload: LoginRequest): Promise<void>;
  logout(): Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [api] = useState<AppApi>(() => createApiClient());
  const [employee, setEmployee] = useState<Employee | null>(null);

  const value = useMemo<AuthContextValue>(
    () => ({
      api,
      employee,
      async login(payload) {
        const result = await api.login(payload);
        setEmployee(result.employee);
      },
      async logout() {
        await api.logout();
        setEmployee(null);
      }
    }),
    [api, employee]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
