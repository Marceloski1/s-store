export type Money = {
  amount: string
  currency: string
}

export type SneakerBadge = "new" | "last-sizes" | "sold-out"

export type SneakerImage = {
  id: string
  url: string | null
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

export interface StorefrontGateway {
  listSneakers(page: number, size: number): Promise<CatalogPage>
  listFeatured(limit: number): Promise<SneakerSummary[]>
  getSneakerBySlug(slug: string): Promise<SneakerDetail | null>
  getFacets(): Promise<CatalogFacets>
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
