import { apiClient } from "@/lib/api/client"
import { unwrap } from "@/lib/api/result"

export const categoryService = {
  async list(page: number, size: number) {
    return unwrap(
      await apiClient.GET("/categories", { params: { query: { page, size } } })
    )
  },
}
