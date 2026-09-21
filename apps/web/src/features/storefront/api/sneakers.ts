import { SneakerSort } from "@/lib/api/types"
import { GENDER_LABELS } from "@/features/catalog/api/labels"
import {
  REFERENCE_PAGE_SIZE,
  toCatalogReferences,
  type CatalogReferences,
} from "@/features/catalog/api/references"
import type {
  CatalogFacets,
  CatalogPage,
  CatalogQuery,
  Colorway,
  SneakerDetail,
  SneakerImage,
  SneakerSummary,
} from "@/features/storefront/api/types"
import { CatalogSort, SneakerBadge } from "@/features/storefront/api/types"
import type { ApiGender, ApiSneaker } from "@/lib/api/types"
import { brandService } from "@/services/catalogs-services/brand"
import { categoryService } from "@/services/catalogs-services/category"
import { facetService } from "@/services/catalogs-services/facet"
import { sneakerService } from "@/services/catalogs-services/sneaker"

const CATALOG_PAGE_SIZE = 9
const NEW_RELEASE_DAYS = 30
const LAST_SIZES_THRESHOLD = 5
const DAY_IN_MS = 24 * 60 * 60 * 1000

const SORT_PARAMS: Record<
  CatalogSort,
  {
    sort: SneakerSort
    descending: boolean
  }
> = {
  [CatalogSort.CREATED_AT]: { sort: SneakerSort.CREATED_AT, descending: true },
  [CatalogSort.PRICE_ASC]: { sort: SneakerSort.PRICE, descending: false },
  [CatalogSort.PRICE_DESC]: { sort: SneakerSort.PRICE, descending: true },
  [CatalogSort.NAME]: { sort: SneakerSort.NAME, descending: false },
  [CatalogSort.RELEASE_DATE]: {
    sort: SneakerSort.RELEASE_DATE,
    descending: true,
  },
}

type ListParams = {
  query?: Partial<CatalogQuery>
  size?: number
}

export function normalizeSize(size: string): string {
  const value = Number(size)
  return Number.isNaN(value) ? size : String(value)
}

async function loadCatalogReferences(): Promise<CatalogReferences> {
  const [brands, categories] = await Promise.all([
    brandService.list(1, REFERENCE_PAGE_SIZE),
    categoryService.list(1, REFERENCE_PAGE_SIZE),
  ])
  return toCatalogReferences(brands.items, categories.items)
}

function isGender(value: string): value is ApiGender {
  return value in GENDER_LABELS
}

function toColorways(sneaker: ApiSneaker): Colorway[] {
  return sneaker.colorways.map((colorway) => ({
    id: colorway.id,
    name: colorway.name,
    colorCode: colorway.color_code,
    sku: colorway.sku,
    price: colorway.effective_price,
    sizes: colorway.sizes.map((variant) => ({
      size: normalizeSize(variant.size),
      stock: variant.stock,
    })),
  }))
}

function toImages(sneaker: ApiSneaker): SneakerImage[] {
  return [...sneaker.images]
    .sort(
      (left, right) =>
        Number(right.is_primary) - Number(left.is_primary) ||
        left.position - right.position
    )
    .map((image, index) => ({
      id: image.id,
      url: image.url,
      alt: image.alt || `${sneaker.name}, vista ${index + 1}`,
      isPrimary: image.is_primary,
    }))
}

function sizeRange(colorways: Colorway[]): string {
  const sizes = colorways
    .flatMap((colorway) =>
      colorway.sizes.map((variant) => Number(variant.size))
    )
    .filter((size) => !Number.isNaN(size))
  if (sizes.length === 0) {
    return "Tallas por confirmar"
  }
  return `Tallas ${Math.min(...sizes)}–${Math.max(...sizes)}`
}

function availableStock(colorways: Colorway[]): number {
  return colorways.reduce(
    (total, colorway) =>
      total + colorway.sizes.reduce((sum, variant) => sum + variant.stock, 0),
    0
  )
}

function isNewRelease(releaseDate: string | null | undefined): boolean {
  if (!releaseDate) {
    return false
  }
  const released = new Date(`${releaseDate}T00:00:00`).getTime()
  const age = Date.now() - released
  return age >= 0 && age <= NEW_RELEASE_DAYS * DAY_IN_MS
}

function badgeFor(
  sneaker: ApiSneaker,
  colorways: Colorway[]
): SneakerBadge | null {
  const stock = availableStock(colorways)
  if (stock === 0) {
    return SneakerBadge.SOLD_OUT
  }
  if (isNewRelease(sneaker.release_date)) {
    return SneakerBadge.NEW
  }
  if (stock <= LAST_SIZES_THRESHOLD) {
    return SneakerBadge.LAST_SIZES
  }
  return null
}

function categorySlugLookup(
  references: CatalogReferences
): (id: string) => string | null {
  const slugs = new Map(
    references.categories.map((category) => [category.id, category.slug])
  )
  return (id) => slugs.get(id) ?? null
}

function toDetail(
  sneaker: ApiSneaker,
  references: CatalogReferences
): SneakerDetail {
  const colorways = toColorways(sneaker)
  const images = toImages(sneaker)
  return {
    id: sneaker.id,
    slug: sneaker.slug,
    name: sneaker.name,
    brand: references.brandName(sneaker.brand_id),
    category: references.categoryName(sneaker.category_id),
    categorySlug: categorySlugLookup(references)(sneaker.category_id),
    gender: GENDER_LABELS[sneaker.gender],
    reference: sneaker.reference ?? colorways[0]?.sku ?? "",
    price: sneaker.base_price,
    colorCodes: colorways.map((colorway) => colorway.colorCode),
    sizeRange: sizeRange(colorways),
    badge: badgeFor(sneaker, colorways),
    image: images[0] ?? null,
    description: sneaker.description,
    usage: sneaker.usage,
    specs: sneaker.specs,
    testimonial: sneaker.testimonial ?? null,
    images,
    colorways,
  }
}

function toSummary(detail: SneakerDetail): SneakerSummary {
  return {
    id: detail.id,
    slug: detail.slug,
    name: detail.name,
    brand: detail.brand,
    category: detail.category,
    gender: detail.gender,
    reference: detail.reference,
    price: detail.price,
    colorCodes: detail.colorCodes,
    sizeRange: detail.sizeRange,
    badge: detail.badge,
    image: detail.image,
  }
}

async function fetchPage({ query = {}, size = CATALOG_PAGE_SIZE }: ListParams) {
  const { sort, descending } = SORT_PARAMS[query.sort ?? CatalogSort.CREATED_AT]
  const currency = query.currency ?? undefined
  const hasPriceFilter = Boolean(currency && (query.minPrice || query.maxPrice))
  return sneakerService.list({
    page: query.page ?? 1,
    size,
    brand: query.brands,
    category: query.categories,
    gender: query.genders,
    shoe_size: query.sizes,
    color: query.colors,
    min_price: hasPriceFilter ? (query.minPrice ?? undefined) : undefined,
    max_price: hasPriceFilter ? (query.maxPrice ?? undefined) : undefined,
    currency: hasPriceFilter ? currency : undefined,
    in_stock: query.inStock,
    q: query.reference ?? query.q ?? undefined,
    sort,
    descending,
  })
}

export async function listSneakers(
  query: Partial<CatalogQuery>
): Promise<CatalogPage> {
  const [page, references] = await Promise.all([
    fetchPage({ query }),
    loadCatalogReferences(),
  ])
  return {
    items: page.items.map((item) => toSummary(toDetail(item, references))),
    total: page.total,
    page: page.page,
    size: page.size,
    pages: Math.max(1, page.pages),
  }
}

export async function listFeatured(limit = 4): Promise<SneakerSummary[]> {
  const [page, references] = await Promise.all([
    fetchPage({ query: { sort: CatalogSort.CREATED_AT }, size: limit }),
    loadCatalogReferences(),
  ])
  return page.items.map((item) => toSummary(toDetail(item, references)))
}

export async function listRelated(
  detail: SneakerDetail,
  limit = 4
): Promise<SneakerSummary[]> {
  const [page, references] = await Promise.all([
    fetchPage({
      query: { categories: detail.categorySlug ? [detail.categorySlug] : [] },
      size: limit + 1,
    }),
    loadCatalogReferences(),
  ])
  return page.items
    .filter((item) => item.slug !== detail.slug)
    .slice(0, limit)
    .map((item) => toSummary(toDetail(item, references)))
}

export async function getSneakerBySlug(
  slug: string
): Promise<SneakerDetail | null> {
  const [sneaker, references] = await Promise.all([
    sneakerService.getBySlug(slug),
    loadCatalogReferences(),
  ])
  return sneaker ? toDetail(sneaker, references) : null
}

export async function getFacets(): Promise<CatalogFacets> {
  const data = await facetService.get()
  return {
    brands: data.brands,
    categories: data.categories,
    genders: data.genders.map((gender) => ({
      ...gender,
      label: isGender(gender.value)
        ? GENDER_LABELS[gender.value]
        : gender.label,
    })),
    sizes: data.sizes.map((size) => ({ ...size, available: true })),
    colors: data.colors.map((color) => ({
      value: color.value,
      label: color.label,
    })),
    currencies: data.currencies,
  }
}
