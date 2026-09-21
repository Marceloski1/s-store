import type { ApiRole, ApiUser } from "@/lib/api/types"

export type AdminNavKey = "sneakers" | "marcas" | "usuarios"

export const ADMIN_NAV = [
  { key: "sneakers", label: "Sneakers", href: "/admin", role: "ADMIN" },
  {
    key: "marcas",
    label: "Marcas y categorías",
    href: "/admin/marcas",
    role: "ADMIN",
  },
  {
    key: "usuarios",
    label: "Usuarios",
    href: "/admin/usuarios",
    role: "SUPER_ADMIN",
  },
] as const satisfies readonly {
  key: AdminNavKey
  label: string
  href: string
  role: ApiRole
}[]

export function navFor(user: ApiUser | null) {
  return ADMIN_NAV.filter((item) => item.role === user?.role)
}

export function initialsOf(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("")
}
