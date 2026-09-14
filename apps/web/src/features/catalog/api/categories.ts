import type { NamedResourceGateway } from "@/features/catalog/api/types"
import { apiClient } from "@/lib/api/client"
import { ApiError } from "@/lib/api/errors"

export const categoriesGateway: NamedResourceGateway = {
  async list(page, size) {
    const { data, error } = await apiClient.GET("/categories", {
      params: { query: { page, size } },
    })
    if (error) throw new ApiError(error)
    return data
  },
  async create(input) {
    const { data, error } = await apiClient.POST("/categories", {
      body: input,
    })
    if (error) throw new ApiError(error)
    return data
  },
  async update(id, input) {
    const { data, error } = await apiClient.PUT("/categories/{category_id}", {
      params: { path: { category_id: id } },
      body: input,
    })
    if (error) throw new ApiError(error)
    return data
  },
  async remove(id) {
    const { error } = await apiClient.DELETE("/categories/{category_id}", {
      params: { path: { category_id: id } },
    })
    if (error) throw new ApiError(error)
  },
}
