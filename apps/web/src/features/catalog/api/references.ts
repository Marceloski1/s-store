import { brandsGateway } from "@/features/catalog/api/brands"
import { categoriesGateway } from "@/features/catalog/api/categories"
import type { NamedResource } from "@/features/catalog/api/types"

const REFERENCE_PAGE_SIZE = 100

export type CatalogReferences = {
  brands: NamedResource[]
  categories: NamedResource[]
  brandName: (id: string) => string
  categoryName: (id: string) => string
}

function nameLookup(items: NamedResource[]): (id: string) => string {
  const names = new Map(items.map((item) => [item.id, item.name]))
  return (id) => names.get(id) ?? ""
}

export async function loadCatalogReferences(): Promise<CatalogReferences> {
  const [brands, categories] = await Promise.all([
    brandsGateway.list(1, REFERENCE_PAGE_SIZE),
    categoriesGateway.list(1, REFERENCE_PAGE_SIZE),
  ])
  return {
    brands: brands.items,
    categories: categories.items,
    brandName: nameLookup(brands.items),
    categoryName: nameLookup(categories.items),
  }
}
