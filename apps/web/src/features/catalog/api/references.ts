import type { NamedResource } from "@/features/catalog/api/types"

export type CatalogReferences = {
  brands: NamedResource[]
  categories: NamedResource[]
  brandName: (id: string) => string
  categoryName: (id: string) => string
}

export const REFERENCE_PAGE_SIZE = 100

function nameLookup(items: NamedResource[]): (id: string) => string {
  const names = new Map(items.map((item) => [item.id, item.name]))
  return (id) => names.get(id) ?? ""
}

export function toCatalogReferences(
  brands: NamedResource[],
  categories: NamedResource[]
): CatalogReferences {
  return {
    brands,
    categories,
    brandName: nameLookup(brands),
    categoryName: nameLookup(categories),
  }
}
