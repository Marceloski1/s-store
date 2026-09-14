import type { NamedResourceGateway } from "@/features/catalog/api/types"
import { apiClient } from "@/lib/api/client"
import { ApiError } from "@/lib/api/errors"

export const brandsGateway: NamedResourceGateway = {
  async list(page, size) {
    const { data, error } = await apiClient.GET("/brands", {
      params: { query: { page, size } },
    })
    if (error) throw new ApiError(error)
    return data
  },
  async create(input) {
    const { data, error } = await apiClient.POST("/brands", { body: input })
    if (error) throw new ApiError(error)
    return data
  },
  async update(id, input) {
    const { data, error } = await apiClient.PUT("/brands/{brand_id}", {
      params: { path: { brand_id: id } },
      body: input,
    })
    if (error) throw new ApiError(error)
    return data
  },
  async remove(id) {
    const { error } = await apiClient.DELETE("/brands/{brand_id}", {
      params: { path: { brand_id: id } },
    })
    if (error) throw new ApiError(error)
  },
}
