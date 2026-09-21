import { apiClient } from "@/lib/api/client"
import { ensureOk, unwrap } from "@/lib/api/result"
import type {
  ApiCreateUserRequest,
  ApiUpdateUserRequest,
} from "@/lib/api/types"

function userPath(userId: string) {
  return { params: { path: { user_id: userId } } }
}

export const userService = {
  async list(page: number, size: number) {
    return unwrap(
      await apiClient.GET("/users", { params: { query: { page, size } } })
    )
  },
  async create(body: ApiCreateUserRequest) {
    return unwrap(await apiClient.POST("/users", { body }))
  },
  async update(userId: string, body: ApiUpdateUserRequest) {
    return unwrap(
      await apiClient.PATCH("/users/{user_id}", { ...userPath(userId), body })
    )
  },
  async remove(userId: string) {
    ensureOk(await apiClient.DELETE("/users/{user_id}", userPath(userId)))
  },
}
