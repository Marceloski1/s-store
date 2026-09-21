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
  REFERENCE_PAGE_SIZE,
  toCatalogReferences,
  type CatalogReferences,
} from "@/features/catalog/api/references"
import type {
  ApiColorwayRequest,
  ApiSneaker,
  ApiSneakerRequest,
} from "@/lib/api/types"
import { brandService } from "@/services/admin-services/brand"
import { categoryService } from "@/services/admin-services/category"
import { sneakerService } from "@/services/admin-services/sneaker"

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

export async function loadAdminReferences(): Promise<CatalogReferences> {
  const [brands, categories] = await Promise.all([
    brandService.list(1, REFERENCE_PAGE_SIZE),
    categoryService.list(1, REFERENCE_PAGE_SIZE),
  ])
  return toCatalogReferences(brands.items, categories.items)
}

function listPage(page: number, size: number, status: SneakerStatus | null) {
  return sneakerService.list({
    page,
    size,
    status,
    sort: "created_at",
    descending: true,
  })
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
    loadAdminReferences(),
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

export function colorwayRequest(input: ColorwayInput): ApiColorwayRequest {
  return {
    name: input.name,
    color_code: input.colorCode,
    sku: input.sku,
    price_override: blankToNull(input.priceOverride),
  }
}
