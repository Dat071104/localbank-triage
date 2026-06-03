import type { Role } from "../api/types";

export function RoleGuard({
  role,
  allowed,
  children,
  fallback = null
}: {
  role: Role;
  allowed: Role[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  return allowed.includes(role) ? <>{children}</> : <>{fallback}</>;
}
