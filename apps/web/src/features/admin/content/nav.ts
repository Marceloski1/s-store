import type { ApiRole, ApiUser } from "@/lib/api/types"

export enum AdminSection {
  SNEAKERS = "SNEAKERS",
  BRANDS = "BRANDS",
  USERS = "USERS",
}

export const ADMIN_SECTION_LABELS: Record<AdminSection, string> = {
  [AdminSection.SNEAKERS]: "Sneakers",
  [AdminSection.BRANDS]: "Marcas y categorías",
  [AdminSection.USERS]: "Usuarios",
}

const ADMIN_SECTION_ROUTES: Record<
  AdminSection,
  { href: string; role: ApiRole }
> = {
  [AdminSection.SNEAKERS]: { href: "/admin", role: "ADMIN" },
  [AdminSection.BRANDS]: { href: "/admin/marcas", role: "ADMIN" },
  [AdminSection.USERS]: { href: "/admin/usuarios", role: "SUPER_ADMIN" },
}

export const ADMIN_NAV = Object.values(AdminSection).map((section) => ({
  section,
  label: ADMIN_SECTION_LABELS[section],
  ...ADMIN_SECTION_ROUTES[section],
}))

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
