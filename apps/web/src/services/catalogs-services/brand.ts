import { apiClient } from "@/lib/api/client"
import { unwrap } from "@/lib/api/result"

export const brandService = {
  async list(page: number, size: number) {
    return unwrap(
      await apiClient.GET("/brands", { params: { query: { page, size } } })
    )
  },
}
