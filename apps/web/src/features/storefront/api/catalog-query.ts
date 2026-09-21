import { CatalogSort, type CatalogQuery } from "@/features/storefront/api/types"

function optional(params: URLSearchParams, key: string): string | null {
  const value = params.get(key)?.trim()
  return value ? value : null
}

function isSort(value: string | null): value is CatalogSort {
  return Object.values<string>(CatalogSort).includes(value ?? "")
}

export function parseCatalogQuery(params: URLSearchParams): CatalogQuery {
  const sort = params.get("sort")
  const page = Number(params.get("page") ?? "1")
  return {
    brands: params.getAll("brand"),
    categories: params.getAll("category"),
    genders: params.getAll("gender"),
    sizes: params.getAll("size"),
    colors: params.getAll("color"),
    minPrice: optional(params, "min_price"),
    maxPrice: optional(params, "max_price"),
    currency: optional(params, "currency"),
    inStock: params.get("in_stock") === "true",
    q: optional(params, "q"),
    reference: optional(params, "reference"),
    sort: isSort(sort) ? sort : CatalogSort.CREATED_AT,
    page: Number.isInteger(page) && page > 0 ? page : 1,
  }
}

export function catalogHref(
  query: CatalogQuery,
  overrides: Partial<CatalogQuery> = {}
): string {
  const next = { ...query, ...overrides }
  const params = new URLSearchParams()
  const lists: [string, string[]][] = [
    ["brand", next.brands],
    ["category", next.categories],
    ["gender", next.genders],
    ["size", next.sizes],
    ["color", next.colors],
  ]
  for (const [key, values] of lists) {
    for (const value of values) {
      params.append(key, value)
    }
  }
  const singles: [string, string | null][] = [
    ["min_price", next.minPrice],
    ["max_price", next.maxPrice],
    ["currency", next.currency],
    ["q", next.q],
    ["reference", next.reference],
  ]
  for (const [key, value] of singles) {
    if (value) {
      params.set(key, value)
    }
  }
  if (next.inStock) {
    params.set("in_stock", "true")
  }
  if (next.sort !== CatalogSort.CREATED_AT) {
    params.set("sort", next.sort)
  }
  if (next.page > 1) {
    params.set("page", String(next.page))
  }
  const search = params.toString()
  return search ? `/sneakers?${search}` : "/sneakers"
}
