import { GENDER_LABELS } from "@/features/catalog/api/labels"
import { Currency, Gender } from "@/lib/api/types"
import { toEnum, toEnums } from "@/lib/enums"
import {
  CatalogSort,
  type CatalogFacets,
  type CatalogQuery,
} from "@/features/storefront/api/types"

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
    genders: toEnums(Gender, params.getAll("gender")),
    sizes: params.getAll("size"),
    colors: params.getAll("color"),
    minPrice: optional(params, "min_price"),
    maxPrice: optional(params, "max_price"),
    currency: toEnum(Currency, params.get("currency")),
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

export type FilterChip = {
  label: string
  href: string
}

type ListFilter = "brands" | "categories" | "genders" | "sizes" | "colors"

function labelFor(options: { value: string; label: string }[], value: string) {
  return options.find((option) => option.value === value)?.label ?? value
}

function without(query: CatalogQuery, key: ListFilter, value: string) {
  return catalogHref(query, {
    [key]: query[key].filter((item) => item !== value),
    page: 1,
  })
}

function priceLabel(query: CatalogQuery): string | null {
  if (!query.minPrice && !query.maxPrice) return null
  const currency = query.currency ? ` ${query.currency}` : ""
  return `Precio ${query.minPrice ?? "0"} – ${query.maxPrice ?? "∞"}${currency}`
}

export function activeFilterChips(
  query: CatalogQuery,
  facets: CatalogFacets
): FilterChip[] {
  const price = priceLabel(query)
  return [
    ...query.brands.map((value) => ({
      label: labelFor(facets.brands, value),
      href: without(query, "brands", value),
    })),
    ...query.categories.map((value) => ({
      label: labelFor(facets.categories, value),
      href: without(query, "categories", value),
    })),
    ...query.genders.map((value) => ({
      label: GENDER_LABELS[value],
      href: without(query, "genders", value),
    })),
    ...query.sizes.map((value) => ({
      label: `Talla EU ${value}`,
      href: without(query, "sizes", value),
    })),
    ...query.colors.map((value) => ({
      label: `Color ${labelFor(facets.colors, value)}`,
      href: without(query, "colors", value),
    })),
    ...(price
      ? [
          {
            label: price,
            href: catalogHref(query, {
              minPrice: null,
              maxPrice: null,
              currency: null,
              page: 1,
            }),
          },
        ]
      : []),
    ...(query.reference
      ? [
          {
            label: `Ref. ${query.reference}`,
            href: catalogHref(query, { reference: null, page: 1 }),
          },
        ]
      : []),
    ...(query.inStock
      ? [
          {
            label: "Solo con stock",
            href: catalogHref(query, { inStock: false, page: 1 }),
          },
        ]
      : []),
  ]
}

export function preservedSearchFields(query: CatalogQuery): [string, string][] {
  return [
    ...query.brands.map((value): [string, string] => ["brand", value]),
    ...query.categories.map((value): [string, string] => ["category", value]),
    ...query.genders.map((value): [string, string] => ["gender", value]),
    ...query.sizes.map((value): [string, string] => ["size", value]),
    ...query.colors.map((value): [string, string] => ["color", value]),
    ...(query.minPrice
      ? [["min_price", query.minPrice] as [string, string]]
      : []),
    ...(query.maxPrice
      ? [["max_price", query.maxPrice] as [string, string]]
      : []),
    ...(query.currency
      ? [["currency", query.currency] as [string, string]]
      : []),
    ...(query.reference
      ? [["reference", query.reference] as [string, string]]
      : []),
    ...(query.inStock ? [["in_stock", "true"] as [string, string]] : []),
  ]
}
