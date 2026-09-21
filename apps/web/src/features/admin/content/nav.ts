export type AdminNavKey = "sneakers" | "marcas"

export const ADMIN_NAV = [
  { key: "sneakers", label: "Sneakers", href: "/admin" },
  { key: "marcas", label: "Marcas y categorías", href: "/admin/marcas" },
] as const satisfies readonly {
  key: AdminNavKey
  label: string
  href: string
}[]

export const ADMIN_USER = {
  name: "Eduardo M.",
  // TODO(007): sustituir por un enum de rol (ADMIN) cuando exista la autenticación
  role: "Administrador",
  initials: "EM",
} as const
