import { apiClient } from "@/lib/api/client"
import { unwrap } from "@/lib/api/result"

function imagePath(sneakerId: string, imageId: string) {
  return { params: { path: { sneaker_id: sneakerId, image_id: imageId } } }
}

export const imageService = {
  async upload(sneakerId: string, file: File, alt: string) {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("alt", alt)
    return unwrap(
      await apiClient.POST("/sneakers/{sneaker_id}/images", {
        params: { path: { sneaker_id: sneakerId } },
        body: { file: "", alt },
        bodySerializer: () => formData,
      })
    )
  },
  async reorder(sneakerId: string, imageIds: string[]) {
    return unwrap(
      await apiClient.PUT("/sneakers/{sneaker_id}/images/order", {
        params: { path: { sneaker_id: sneakerId } },
        body: { image_ids: imageIds },
      })
    )
  },
  async markPrimary(sneakerId: string, imageId: string) {
    return unwrap(
      await apiClient.POST(
        "/sneakers/{sneaker_id}/images/{image_id}/primary",
        imagePath(sneakerId, imageId)
      )
    )
  },
  async remove(sneakerId: string, imageId: string) {
    return unwrap(
      await apiClient.DELETE(
        "/sneakers/{sneaker_id}/images/{image_id}",
        imagePath(sneakerId, imageId)
      )
    )
  },
}
