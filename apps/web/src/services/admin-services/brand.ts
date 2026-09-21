import { apiClient } from "@/lib/api/client"
import { ensureOk, unwrap } from "@/lib/api/result"
import type { ApiBrandRequest } from "@/lib/api/types"

export const brandService = {
  async list(page: number, size: number) {
    return unwrap(
      await apiClient.GET("/brands", { params: { query: { page, size } } })
    )
  },
  async create(input: ApiBrandRequest) {
    return unwrap(await apiClient.POST("/brands", { body: input }))
  },
  async update(id: string, input: ApiBrandRequest) {
    return unwrap(
      await apiClient.PUT("/brands/{brand_id}", {
        params: { path: { brand_id: id } },
        body: input,
      })
    )
  },
  async remove(id: string) {
    ensureOk(
      await apiClient.DELETE("/brands/{brand_id}", {
        params: { path: { brand_id: id } },
      })
    )
  },
}
