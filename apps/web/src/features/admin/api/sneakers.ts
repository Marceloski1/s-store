import type {
  AdminSneakerPage,
  AdminSneakerRow,
  AdminStats,
  ColorwayInput,
  SneakerForm,
  SneakerStatus,
} from "@/features/admin/api/types"
import { primaryImageUrl, sneakerStock } from "@/features/admin/api/types"
import {
  loadCatalogReferences,
  type CatalogReferences,
} from "@/features/catalog/api/references"
import { apiClient } from "@/lib/api/client"
import { ApiError } from "@/lib/api/errors"
import type { ApiSneaker, ApiSneakerRequest } from "@/lib/api/types"

const MAX_PAGE_SIZE = 100
const ADMIN_PAGE_SIZE = 20

function warningFor(sneaker: ApiSneaker): string | null {
  if (!primaryImageUrl(sneaker)) {
    return "falta la foto principal"
  }
  if (sneakerStock(sneaker) === 0) {
    return "sin tallas con stock"
  }
  if (sneaker.status === "archived") {
    return "archivado"
  }
  return null
}

function toRow(
  sneaker: ApiSneaker,
  references: CatalogReferences
): AdminSneakerRow {
  return {
    id: sneaker.id,
    slug: sneaker.slug,
    name: sneaker.name,
    sku: sneaker.reference ?? sneaker.colorways[0]?.sku ?? "Sin referencia",
    brand: references.brandName(sneaker.brand_id),
    category: references.categoryName(sneaker.category_id),
    price: sneaker.base_price,
    colorways: sneaker.colorways.length,
    stock: sneakerStock(sneaker),
    status: sneaker.status,
    updatedAt: sneaker.updated_at,
    imageUrl: primaryImageUrl(sneaker),
    warning: warningFor(sneaker),
  }
}

async function listPage(
  page: number,
  size: number,
  status: SneakerStatus | null
) {
  const { data, error } = await apiClient.GET("/sneakers", {
    params: {
      query: { page, size, status, sort: "created_at", descending: true },
    },
  })
  if (error) throw new ApiError(error)
  return data
}

async function listAll(): Promise<ApiSneaker[]> {
  const first = await listPage(1, MAX_PAGE_SIZE, null)
  const rest = await Promise.all(
    Array.from({ length: Math.max(0, first.pages - 1) }, (_, index) =>
      listPage(index + 2, MAX_PAGE_SIZE, null)
    )
  )
  return [first, ...rest].flatMap((page) => page.items)
}

export async function listAdminSneakers(
  status: SneakerStatus | null,
  page: number
): Promise<AdminSneakerPage> {
  const [result, references] = await Promise.all([
    listPage(page, ADMIN_PAGE_SIZE, status),
    loadCatalogReferences(),
  ])
  return {
    rows: result.items.map((sneaker) => toRow(sneaker, references)),
    total: result.total,
    page: result.page,
    pages: Math.max(1, result.pages),
  }
}

export async function getAdminStats(): Promise<AdminStats> {
  const sneakers = await listAll()
  const count = (status: SneakerStatus) =>
    sneakers.filter((sneaker) => sneaker.status === status).length
  return {
    total: sneakers.length,
    published: count("active"),
    drafts: count("draft"),
    archived: count("archived"),
    outOfStock: sneakers.filter((sneaker) => sneakerStock(sneaker) === 0)
      .length,
  }
}

function blankToNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === "" ? null : trimmed
}

export function formToRequest(form: SneakerForm): ApiSneakerRequest {
  const quote = form.testimonialQuote.trim()
  const author = form.testimonialAuthor.trim()
  return {
    name: form.name,
    slug: blankToNull(form.slug),
    reference: blankToNull(form.reference),
    description: form.description,
    brand_id: form.brandId,
    category_id: form.categoryId,
    gender: form.gender,
    price: form.price,
    currency: form.currency,
    release_date: blankToNull(form.releaseDate),
    specs: {
      material: form.material,
      technology: form.technology,
      weight: form.weight,
      cushioning: form.cushioning,
    },
    usage: form.usage,
    testimonial: quote && author ? { quote, author } : null,
  }
}

function colorwayRequest(input: ColorwayInput) {
  return {
    name: input.name,
    color_code: input.colorCode,
    sku: input.sku,
    price_override: blankToNull(input.priceOverride),
  }
}

function unwrap<T>(result: { data?: T; error?: unknown }): T {
  if (result.error !== undefined || result.data === undefined) {
    throw new ApiError(result.error)
  }
  return result.data
}

function sneakerPath(sneakerId: string) {
  return { params: { path: { sneaker_id: sneakerId } } }
}

export const adminSneakersGateway = {
  async getBySlug(slug: string): Promise<ApiSneaker | null> {
    const { data, error, response } = await apiClient.GET(
      "/sneakers/by-slug/{slug}",
      { params: { path: { slug } } }
    )
    if (response.status === 404) return null
    if (error) throw new ApiError(error)
    return data
  },
  async create(body: ApiSneakerRequest): Promise<ApiSneaker> {
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
  async addColorway(sneakerId: string, input: ColorwayInput) {
    return unwrap(
      await apiClient.POST("/sneakers/{sneaker_id}/colorways", {
        ...sneakerPath(sneakerId),
        body: colorwayRequest(input),
      })
    )
  },
  async updateColorway(
    sneakerId: string,
    colorwayId: string,
    input: ColorwayInput
  ) {
    return unwrap(
      await apiClient.PUT("/sneakers/{sneaker_id}/colorways/{colorway_id}", {
        params: { path: { sneaker_id: sneakerId, colorway_id: colorwayId } },
        body: colorwayRequest(input),
      })
    )
  },
  async removeColorway(sneakerId: string, colorwayId: string) {
    return unwrap(
      await apiClient.DELETE("/sneakers/{sneaker_id}/colorways/{colorway_id}", {
        params: { path: { sneaker_id: sneakerId, colorway_id: colorwayId } },
      })
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
        {
          params: {
            path: { sneaker_id: sneakerId, colorway_id: colorwayId, size },
          },
          body: { stock },
        }
      )
    )
  },
  async removeSize(sneakerId: string, colorwayId: string, size: string) {
    return unwrap(
      await apiClient.DELETE(
        "/sneakers/{sneaker_id}/colorways/{colorway_id}/sizes/{size}",
        {
          params: {
            path: { sneaker_id: sneakerId, colorway_id: colorwayId, size },
          },
        }
      )
    )
  },
  async uploadImage(sneakerId: string, file: File, alt: string) {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("alt", alt)
    return unwrap(
      await apiClient.POST("/sneakers/{sneaker_id}/images", {
        ...sneakerPath(sneakerId),
        body: { file: "", alt },
        bodySerializer: () => formData,
      })
    )
  },
  async reorderImages(sneakerId: string, imageIds: string[]) {
    return unwrap(
      await apiClient.PUT("/sneakers/{sneaker_id}/images/order", {
        ...sneakerPath(sneakerId),
        body: { image_ids: imageIds },
      })
    )
  },
  async markPrimaryImage(sneakerId: string, imageId: string) {
    return unwrap(
      await apiClient.POST("/sneakers/{sneaker_id}/images/{image_id}/primary", {
        params: { path: { sneaker_id: sneakerId, image_id: imageId } },
      })
    )
  },
  async removeImage(sneakerId: string, imageId: string) {
    return unwrap(
      await apiClient.DELETE("/sneakers/{sneaker_id}/images/{image_id}", {
        params: { path: { sneaker_id: sneakerId, image_id: imageId } },
      })
    )
  },
}

export type AdminSneakersGateway = typeof adminSneakersGateway
