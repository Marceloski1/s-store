import { apiClient } from "@/lib/api/client"
import { unwrap } from "@/lib/api/result"
import type { ApiColorwayRequest } from "@/lib/api/types"

function colorwayPath(sneakerId: string, colorwayId: string) {
  return {
    params: { path: { sneaker_id: sneakerId, colorway_id: colorwayId } },
  }
}

function sizePath(sneakerId: string, colorwayId: string, size: string) {
  return {
    params: {
      path: { sneaker_id: sneakerId, colorway_id: colorwayId, size },
    },
  }
}

export const colorwayService = {
  async add(sneakerId: string, body: ApiColorwayRequest) {
    return unwrap(
      await apiClient.POST("/sneakers/{sneaker_id}/colorways", {
        params: { path: { sneaker_id: sneakerId } },
        body,
      })
    )
  },
  async update(
    sneakerId: string,
    colorwayId: string,
    body: ApiColorwayRequest
  ) {
    return unwrap(
      await apiClient.PUT("/sneakers/{sneaker_id}/colorways/{colorway_id}", {
        ...colorwayPath(sneakerId, colorwayId),
        body,
      })
    )
  },
  async remove(sneakerId: string, colorwayId: string) {
    return unwrap(
      await apiClient.DELETE(
        "/sneakers/{sneaker_id}/colorways/{colorway_id}",
        colorwayPath(sneakerId, colorwayId)
      )
    )
  },
  async setSizeStock(
    sneakerId: string,
    colorwayId: string,
    size: string,
    stock: number
  ) {
    return unwrap(
      await apiClient.PUT(
        "/sneakers/{sneaker_id}/colorways/{colorway_id}/sizes/{size}",
        { ...sizePath(sneakerId, colorwayId, size), body: { stock } }
      )
    )
  },
  async removeSize(sneakerId: string, colorwayId: string, size: string) {
    return unwrap(
      await apiClient.DELETE(
        "/sneakers/{sneaker_id}/colorways/{colorway_id}/sizes/{size}",
        sizePath(sneakerId, colorwayId, size)
      )
    )
  },
}
