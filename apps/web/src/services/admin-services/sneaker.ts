import { apiClient } from "@/lib/api/client"
import { unwrap, unwrapOrNull } from "@/lib/api/result"
import type {
  ApiSneakerRequest,
  ApiSneakerSort,
  ApiSneakerStatus,
} from "@/lib/api/types"

type SneakerListQuery = {
  page: number
  size: number
  status?: ApiSneakerStatus | null
  sort?: ApiSneakerSort
  descending?: boolean
}

function sneakerPath(sneakerId: string) {
  return { params: { path: { sneaker_id: sneakerId } } }
}

export const sneakerService = {
  async list(query: SneakerListQuery) {
    return unwrap(await apiClient.GET("/sneakers", { params: { query } }))
  },
  async getBySlug(slug: string) {
    return unwrapOrNull(
      await apiClient.GET("/sneakers/by-slug/{slug}", {
        params: { path: { slug } },
      })
    )
  },
  async create(body: ApiSneakerRequest) {
    return unwrap(await apiClient.POST("/sneakers", { body }))
  },
  async update(sneakerId: string, body: ApiSneakerRequest) {
    return unwrap(
      await apiClient.PUT("/sneakers/{sneaker_id}", {
        ...sneakerPath(sneakerId),
        body,
      })
    )
  },
  async publish(sneakerId: string) {
    return unwrap(
      await apiClient.POST(
        "/sneakers/{sneaker_id}/publish",
        sneakerPath(sneakerId)
      )
    )
  },
  async archive(sneakerId: string) {
    return unwrap(
      await apiClient.POST(
        "/sneakers/{sneaker_id}/archive",
        sneakerPath(sneakerId)
      )
    )
  },
  async unarchive(sneakerId: string) {
    return unwrap(
      await apiClient.POST(
        "/sneakers/{sneaker_id}/unarchive",
        sneakerPath(sneakerId)
      )
    )
  },
}
