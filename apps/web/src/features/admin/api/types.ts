import type { SneakerStatus } from "@/lib/catalog-sample"

export type { SneakerStatus }

export type AdminMoney = {
  amount: string
  currency: string
}

export type AdminSneakerRow = {
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
  warning: string | null
}

export type AdminStats = {
  total: number
  published: number
  drafts: number
  outOfStock: number
}

export type AdminSizeRow = {
  size: string
  stock: number
}

export type AdminColorway = {
  id: string
  name: string
  colorCode: string
  sku: string
  priceOverride: string | null
  sizes: AdminSizeRow[]
}

export type AdminImageSlot = {
  id: string
  isPrimary: boolean
}

export type PublishCheck = {
  label: string
  state: "ok" | "pending"
}

export type AdminSneakerDraft = {
  slug: string
  name: string
  description: string
  brand: string
  category: string
  gender: string
  price: AdminMoney
  releaseDate: string
  specs: {
    material: string
    technology: string
    weight: string
    cushioning: string
  }
  usage: string
  testimonialQuote: string
  testimonialAuthor: string
  colorways: AdminColorway[]
  images: AdminImageSlot[]
  status: SneakerStatus
  stock: number
  updatedAt: string
  checks: PublishCheck[]
}

export const STATUS_LABELS: Record<SneakerStatus, string> = {
  draft: "Borrador",
  active: "Publicado",
  archived: "Archivado",
}

export function formatAdminMoney(price: AdminMoney): string {
  return `${price.amount.replace(".", ",")} ${price.currency}`
}

export function formatAdminDate(isoDate: string): string {
  return new Intl.DateTimeFormat("es", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${isoDate}T00:00:00`))
}
