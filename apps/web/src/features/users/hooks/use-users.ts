import { useState } from "react"

import type {
  CreateUserValues,
  ResetPasswordValues,
} from "@/features/auth/api/schemas"
import { toErrorMessage } from "@/lib/api/errors"
import type { ApiUser } from "@/lib/api/types"
import { userService } from "@/services/admin-services/user"

export function useUsers(initialUsers: ApiUser[]) {
  const [users, setUsers] = useState(initialUsers)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  async function mutate(
    action: () => Promise<void>,
    successMessage: string
  ): Promise<boolean> {
    setIsSaving(true)
    setNotice(null)
    try {
      await action()
      setError(null)
      setNotice(successMessage)
      return true
    } catch (reason) {
      setError(toErrorMessage(reason))
      return false
    } finally {
      setIsSaving(false)
    }
  }

  function replace(updated: ApiUser) {
    setUsers((current) =>
      current.map((user) => (user.id === updated.id ? updated : user))
    )
  }

  return {
    users,
    isSaving,
    error,
    notice,
    create: (values: CreateUserValues) =>
      mutate(async () => {
        const created = await userService.create(values)
        setUsers((current) => [...current, created])
      }, `Administrador ${values.name} creado`),
    toggleActive: (user: ApiUser) =>
      mutate(
        async () =>
          replace(
            await userService.update(user.id, { is_active: !user.is_active })
          ),
        user.is_active ? `${user.name} desactivado` : `${user.name} activado`
      ),
    resetPassword: (user: ApiUser, values: ResetPasswordValues) =>
      mutate(
        async () =>
          replace(
            await userService.update(user.id, { password: values.password })
          ),
        `Contraseña de ${user.name} actualizada`
      ),
    remove: (user: ApiUser) =>
      mutate(async () => {
        await userService.remove(user.id)
        setUsers((current) => current.filter((item) => item.id !== user.id))
      }, `${user.name} eliminado`),
  }
}
