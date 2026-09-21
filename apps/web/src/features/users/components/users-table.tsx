import { Role } from "@/lib/api/types"
import { useState } from "react"

import { Form, FormField } from "@workspace/ui/components/form"

import { formatAdminDate } from "@/features/admin/api/types"
import {
  fieldClass,
  sectionClass,
} from "@/features/admin/components/editor-styles"
import { ROLE_LABELS } from "@/features/auth/api/permissions"
import {
  resetPasswordSchema,
  type ResetPasswordValues,
} from "@/features/auth/api/schemas"
import type { ApiUser } from "@/lib/api/types"

type UsersTableProps = {
  users: ApiUser[]
  currentUserId: string
  disabled: boolean
  onToggleActive: (user: ApiUser) => void
  onResetPassword: (
    user: ApiUser,
    values: ResetPasswordValues
  ) => Promise<boolean>
  onRemove: (user: ApiUser) => void
}

const headerClass =
  "px-3 py-3 text-left text-[11px] font-extrabold tracking-[0.1em] text-muted-foreground uppercase"
const actionClass =
  "h-9 border border-input bg-card px-3 text-[11px] font-extrabold tracking-[0.06em] uppercase hover:bg-muted disabled:opacity-60"

export function UsersTable({
  users,
  currentUserId,
  disabled,
  onToggleActive,
  onResetPassword,
  onRemove,
}: UsersTableProps) {
  const [resettingId, setResettingId] = useState<string | null>(null)

  return (
    <section className={sectionClass}>
      <div className="border-b border-border px-6 py-4">
        <h2 className="text-[17px] font-extrabold">Usuarios del panel</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse">
          <thead>
            <tr className="bg-muted">
              <th className={`${headerClass} pl-6`}>Nombre</th>
              <th className={headerClass}>Rol</th>
              <th className={headerClass}>Estado</th>
              <th className={headerClass}>Alta</th>
              <th className={`${headerClass} pr-6 text-right`}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => {
              const manageable =
                user.role === Role.ADMIN && user.id !== currentUserId
              return (
                <tr
                  key={user.id}
                  className="border-t border-border/60 align-top"
                >
                  <td className="py-3 pr-3 pl-6">
                    <div className="flex flex-col gap-0.5">
                      <span className="text-sm font-bold">{user.name}</span>
                      <span className="text-[12px] text-muted-foreground">
                        {user.email}
                      </span>
                    </div>
                  </td>
                  <td className="px-3 py-3 text-[13px] font-semibold">
                    {ROLE_LABELS[user.role]}
                  </td>
                  <td className="px-3 py-3">
                    <span
                      className={
                        user.is_active
                          ? "bg-success/15 px-2 py-1 text-[11px] font-extrabold tracking-[0.06em] text-success uppercase"
                          : "bg-muted px-2 py-1 text-[11px] font-extrabold tracking-[0.06em] text-muted-foreground uppercase"
                      }
                    >
                      {user.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td className="px-3 py-3 text-[13px] whitespace-nowrap text-muted-foreground">
                    {formatAdminDate(user.created_at)}
                  </td>
                  <td className="py-3 pr-6 pl-3">
                    {manageable ? (
                      <div className="flex flex-col items-end gap-2">
                        <div className="flex flex-wrap justify-end gap-2">
                          <button
                            type="button"
                            disabled={disabled}
                            onClick={() => onToggleActive(user)}
                            className={actionClass}
                          >
                            {user.is_active ? "Desactivar" : "Activar"}
                          </button>
                          <button
                            type="button"
                            disabled={disabled}
                            aria-expanded={resettingId === user.id}
                            onClick={() =>
                              setResettingId((current) =>
                                current === user.id ? null : user.id
                              )
                            }
                            className={actionClass}
                          >
                            Contraseña
                          </button>
                          <button
                            type="button"
                            disabled={disabled}
                            onClick={() => {
                              if (
                                window.confirm(
                                  `¿Eliminar a ${user.name}? Perderá el acceso al panel.`
                                )
                              ) {
                                onRemove(user)
                              }
                            }}
                            className={`${actionClass} text-destructive`}
                          >
                            Eliminar
                          </button>
                        </div>
                        {resettingId === user.id && (
                          <Form
                            schema={resetPasswordSchema}
                            defaultValues={{ password: "" }}
                            disabled={disabled}
                            onSubmit={async (values) => {
                              if (await onResetPassword(user, values)) {
                                setResettingId(null)
                              }
                            }}
                            className="flex items-start gap-2"
                          >
                            <FormField<ResetPasswordValues, "password">
                              name="password"
                              render={({ field, control }) => (
                                <input
                                  {...control}
                                  {...field}
                                  type="password"
                                  autoComplete="new-password"
                                  aria-label={`Nueva contraseña para ${user.name}`}
                                  placeholder="Nueva contraseña"
                                  className={`${fieldClass} h-9 w-56 aria-invalid:border-destructive`}
                                />
                              )}
                            />
                            <button
                              type="submit"
                              disabled={disabled}
                              className="h-9 bg-primary px-3 text-[11px] font-extrabold tracking-[0.06em] text-primary-foreground uppercase hover:bg-primary/90 disabled:opacity-60"
                            >
                              Guardar
                            </button>
                          </Form>
                        )}
                      </div>
                    ) : (
                      <span className="block text-right text-[12px] text-muted-foreground">
                        {user.id === currentUserId ? "Tu cuenta" : "Protegido"}
                      </span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
