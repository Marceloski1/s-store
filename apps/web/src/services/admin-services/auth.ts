import { apiClient } from "@/lib/api/client"
import { ApiError } from "@/lib/api/errors"
import { ensureOk, unwrap } from "@/lib/api/result"

export const authService = {
  async login(email: string, password: string) {
    return unwrap(
      await apiClient.POST("/auth/login", { body: { email, password } })
    )
  },
  async logout() {
    ensureOk(await apiClient.POST("/auth/logout"))
  },
  async me() {
    const result = await apiClient.GET("/auth/me")
    if (result.response.status === 401) return null
    if (result.error !== undefined) throw new ApiError(result.error)
    return result.data ?? null
  },
}
