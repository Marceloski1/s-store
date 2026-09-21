import { Role } from "@/lib/api/types"
import type { ApiRole, ApiUser } from "@/lib/api/types"

export const LOGIN_PATH = "/admin/login"
export const LOGOUT_PATH = "/admin/logout"

export const ROLE_HOME: Record<ApiRole, string> = {
  [Role.ADMIN]: "/admin",
  [Role.SUPER_ADMIN]: "/admin/usuarios",
}

export const ROLE_LABELS: Record<ApiRole, string> = {
  [Role.ADMIN]: "Administrador",
  [Role.SUPER_ADMIN]: "Superadministrador",
}

type RouteRule = {
  prefix: string
  roles: readonly ApiRole[] | "public" | "session"
}

const ROUTE_RULES: readonly RouteRule[] = [
  { prefix: LOGIN_PATH, roles: "public" },
  { prefix: LOGOUT_PATH, roles: "session" },
  { prefix: "/admin/usuarios", roles: [Role.SUPER_ADMIN] },
  { prefix: "/admin", roles: [Role.ADMIN] },
]

function matches(path: string, prefix: string): boolean {
  return path === prefix || path.startsWith(`${prefix}/`)
}

export function isAdminPath(path: string): boolean {
  return matches(path, "/admin")
}

const NEXT_BASE = "http://local"

export function safeNextPath(next: string | null): string | null {
  if (!next || !next.startsWith("/")) return null
  const url = new URL(next, NEXT_BASE)
  if (url.origin !== NEXT_BASE || !isAdminPath(url.pathname)) return null
  return `${url.pathname}${url.search}`
}

export function resolveAdminRedirect(
  path: string,
  search: string,
  user: ApiUser | null
): string | null {
  const rule = ROUTE_RULES.find((item) => matches(path, item.prefix))
  if (!rule) return null
  if (rule.roles === "public") {
    return user ? ROLE_HOME[user.role] : null
  }
  if (!user) {
    return `${LOGIN_PATH}?next=${encodeURIComponent(`${path}${search}`)}`
  }
  if (rule.roles === "session" || rule.roles.includes(user.role)) return null
  return ROLE_HOME[user.role]
}
