import type {
  ApiColorway,
  ApiGender,
  ApiSneaker,
  ApiSneakerStatus,
} from "@/lib/api/types"

export type SneakerStatus = ApiSneakerStatus

export type AdminMoney = {
  amount: string
  currency: string
}

export type AdminSneakerRow = {
  id: string
  slug: string
  name: string
  sku: string
  brand: string
  category: string
  price: AdminMoney
  colorways: number
  stock: number
  status: SneakerStatus
  updatedAt: string
  imageUrl: string | null
  warning: string | null
}

export type AdminSneakerPage = {
  rows: AdminSneakerRow[]
  total: number
  page: number
  pages: number
}

export type AdminStats = {
  total: number
  published: number
  drafts: number
  archived: number
  outOfStock: number
}

export type AdminOption = {
  value: string
  label: string
}

export function toAdminOptions(
  items: { id: string; name: string }[]
): AdminOption[] {
  return items.map((item) => ({ value: item.id, label: item.name }))
}

export type PublishCheck = {
  label: string
  state: "ok" | "pending"
}

export type SneakerForm = {
  name: string
  slug: string
  reference: string
  description: string
  brandId: string
  categoryId: string
  gender: ApiGender
  price: string
  currency: string
  releaseDate: string
  material: string
  technology: string
  weight: string
  cushioning: string
  usage: string
  testimonialQuote: string
  testimonialAuthor: string
}

export type ColorwayInput = {
  name: string
  colorCode: string
  sku: string
  priceOverride: string
}

export const STATUS_LABELS: Record<SneakerStatus, string> = {
  draft: "Borrador",
  active: "Publicado",
  archived: "Archivado",
}

export const STATUS_TRANSITIONS: Record<SneakerStatus, SneakerStatus[]> = {
  draft: ["active"],
  active: ["archived"],
  archived: ["draft"],
}

export const MAX_IMAGES = 8
export const MAX_IMAGE_BYTES = 5 * 1024 * 1024
export const DESCRIPTION_MAX_LENGTH = 2000

export function formatAdminMoney(price: AdminMoney): string {
  return `${price.amount.replace(".", ",")} ${price.currency}`
}

export function formatAdminDate(isoDate: string): string {
  const date =
    isoDate.length === 10 ? new Date(`${isoDate}T00:00:00`) : new Date(isoDate)
  return new Intl.DateTimeFormat("es", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date)
}

export function formatSize(size: string): string {
  return size.endsWith(".0") ? size.slice(0, -2) : size
}

export function colorwayStock(colorway: ApiColorway): number {
  return colorway.sizes.reduce((total, variant) => total + variant.stock, 0)
}

export function sneakerStock(sneaker: ApiSneaker): number {
  return sneaker.colorways.reduce(
    (total, colorway) => total + colorwayStock(colorway),
    0
  )
}

export function primaryImageUrl(sneaker: ApiSneaker): string | null {
  return sneaker.images.find((image) => image.is_primary)?.url ?? null
}

export function publishChecks(sneaker: ApiSneaker): PublishCheck[] {
  const stock = sneakerStock(sneaker)
  return [
    {
      label: "Tiene foto principal",
      state: primaryImageUrl(sneaker) ? "ok" : "pending",
    },
    {
      label: "Al menos un color con tallas",
      state: sneaker.colorways.some((colorway) => colorway.sizes.length > 0)
        ? "ok"
        : "pending",
    },
    {
      label: stock > 0 ? `${stock} pares en stock` : "Sin pares en stock",
      state: stock > 0 ? "ok" : "pending",
    },
  ]
}

export function emptySneakerForm(
  brandId: string,
  categoryId: string
): SneakerForm {
  return {
    name: "",
    slug: "",
    reference: "",
    description: "",
    brandId,
    categoryId,
    gender: "unisex",
    price: "",
    currency: "USD",
    releaseDate: "",
    material: "",
    technology: "",
    weight: "",
    cushioning: "",
    usage: "",
    testimonialQuote: "",
    testimonialAuthor: "",
  }
}

export function sneakerToForm(sneaker: ApiSneaker): SneakerForm {
  return {
    name: sneaker.name,
    slug: sneaker.slug,
    reference: sneaker.reference ?? "",
    description: sneaker.description,
    brandId: sneaker.brand_id,
    categoryId: sneaker.category_id,
    gender: sneaker.gender,
    price: sneaker.base_price.amount,
    currency: sneaker.base_price.currency,
    releaseDate: sneaker.release_date ?? "",
    material: sneaker.specs.material,
    technology: sneaker.specs.technology,
    weight: sneaker.specs.weight,
    cushioning: sneaker.specs.cushioning,
    usage: sneaker.usage,
    testimonialQuote: sneaker.testimonial?.quote ?? "",
    testimonialAuthor: sneaker.testimonial?.author ?? "",
  }
}

export function colorwayToInput(colorway: ApiColorway): ColorwayInput {
  return {
    name: colorway.name,
    colorCode: colorway.color_code,
    sku: colorway.sku,
    priceOverride: colorway.price_override?.amount ?? "",
  }
}

export function slugify(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 120)
    .replace(/-+$/g, "")
}
