import { useState } from "react"

import type { LoginValues } from "@/features/auth/api/schemas"
import { ROLE_HOME } from "@/features/auth/api/permissions"
import { toErrorMessage } from "@/lib/api/errors"
import { authService } from "@/services/admin-services/auth"

export function useLogin(nextPath: string | null) {
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function login(values: LoginValues) {
    setIsSubmitting(true)
    setError(null)
    try {
      const user = await authService.login(values.email, values.password)
      window.location.assign(nextPath ?? ROLE_HOME[user.role])
    } catch (reason) {
      setError(toErrorMessage(reason))
      setIsSubmitting(false)
    }
  }

  return { error, isSubmitting, login }
}
