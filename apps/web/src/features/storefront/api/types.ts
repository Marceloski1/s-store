export type Money = {
  amount: string
  currency: string
}

export enum SneakerBadge {
  NEW = "NEW",
  LAST_SIZES = "LAST_SIZES",
  SOLD_OUT = "SOLD_OUT",
}

export const SNEAKER_BADGE_LABELS: Record<SneakerBadge, string> = {
  [SneakerBadge.NEW]: "Nuevo",
  [SneakerBadge.LAST_SIZES]: "Últimas tallas",
  [SneakerBadge.SOLD_OUT]: "Sin stock",
}

export type SneakerImage = {
  id: string
  url: string
  alt: string
  isPrimary: boolean
}

export type SizeVariant = {
  size: string
  stock: number
}

export type Colorway = {
  id: string
  name: string
  colorCode: string
  sku: string
  price: Money
  sizes: SizeVariant[]
}

export type SpecSheet = {
  material: string
  technology: string
  weight: string
  cushioning: string
}

export type Testimonial = {
  quote: string
  author: string
}

export type SneakerSummary = {
  id: string
  slug: string
  name: string
  brand: string
  category: string
  gender: string
  reference: string
  price: Money
  colorCodes: string[]
  sizeRange: string
  badge: SneakerBadge | null
  image: SneakerImage | null
}

export type SneakerDetail = SneakerSummary & {
  categorySlug: string | null
  description: string
  usage: string
  specs: SpecSheet
  testimonial: Testimonial | null
  images: SneakerImage[]
  colorways: Colorway[]
}

export type CatalogFacet = {
  value: string
  label: string
  count: number
  available?: boolean
}

export type CatalogFacets = {
  brands: CatalogFacet[]
  categories: CatalogFacet[]
  genders: CatalogFacet[]
  sizes: CatalogFacet[]
  colors: { value: string; label: string }[]
  currencies: string[]
}

export type CatalogPage = {
  items: SneakerSummary[]
  total: number
  page: number
  size: number
  pages: number
}

export enum CatalogSort {
  CREATED_AT = "CREATED_AT",
  PRICE_ASC = "PRICE_ASC",
  PRICE_DESC = "PRICE_DESC",
  NAME = "NAME",
  RELEASE_DATE = "RELEASE_DATE",
}

export const CATALOG_SORT_LABELS: Record<CatalogSort, string> = {
  [CatalogSort.CREATED_AT]: "Más recientes",
  [CatalogSort.PRICE_ASC]: "Precio: de menor a mayor",
  [CatalogSort.PRICE_DESC]: "Precio: de mayor a menor",
  [CatalogSort.NAME]: "Nombre: A – Z",
  [CatalogSort.RELEASE_DATE]: "Fecha de lanzamiento",
}

export type CatalogQuery = {
  brands: string[]
  categories: string[]
  genders: string[]
  sizes: string[]
  colors: string[]
  minPrice: string | null
  maxPrice: string | null
  currency: string | null
  inStock: boolean
  q: string | null
  reference: string | null
  sort: CatalogSort
  page: number
}

export function hasSpecs(specs: SpecSheet): boolean {
  return Object.values(specs).some((value) => value.length > 0)
}

export function formatMoney(price: Money): string {
  return `${price.amount.replace(".", ",")} ${price.currency}`
}

export function totalStock(colorways: Colorway[]): number {
  return colorways.reduce(
    (total, colorway) =>
      total + colorway.sizes.reduce((sum, size) => sum + size.stock, 0),
    0
  )
}
