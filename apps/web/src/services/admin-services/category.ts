import { apiClient } from "@/lib/api/client"
import { ensureOk, unwrap } from "@/lib/api/result"
import type { ApiCategoryRequest } from "@/lib/api/types"

export const categoryService = {
  async list(page: number, size: number) {
    return unwrap(
      await apiClient.GET("/categories", { params: { query: { page, size } } })
    )
  },
  async create(input: ApiCategoryRequest) {
    return unwrap(await apiClient.POST("/categories", { body: input }))
  },
  async update(id: string, input: ApiCategoryRequest) {
    return unwrap(
      await apiClient.PUT("/categories/{category_id}", {
        params: { path: { category_id: id } },
        body: input,
      })
    )
  },
  async remove(id: string) {
    ensureOk(
      await apiClient.DELETE("/categories/{category_id}", {
        params: { path: { category_id: id } },
      })
    )
  },
}
