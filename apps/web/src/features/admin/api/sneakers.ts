import type {
  AdminColorway,
  AdminSneakerDraft,
  AdminSneakerRow,
  AdminStats,
  PublishCheck,
} from "@/features/admin/api/types"
import {
  CATALOG_SEEDS,
  seedStock,
  type SneakerSeed,
} from "@/lib/catalog-sample"

function warningFor(seed: SneakerSeed): string | null {
  if (seed.imageCount === 0) {
    return "falta la foto principal"
  }
  if (seedStock(seed) === 0) {
    return "sin tallas con stock"
  }
  if (seed.status === "archived") {
    // TODO(001): confirmar si un sneaker archivado debe mostrarse como aviso en el listado
    return "archivado"
  }
  return null
}

function toRow(seed: SneakerSeed): AdminSneakerRow {
  return {
    slug: seed.slug,
    name: seed.name,
    sku: seed.reference,
    brand: seed.brand,
    category: seed.category,
    price: { amount: seed.amount, currency: seed.currency },
    colorways: seed.colorways.length,
    stock: seedStock(seed),
    status: seed.status,
    updatedAt: seed.updatedAt,
    warning: warningFor(seed),
  }
}

function toColorways(seed: SneakerSeed): AdminColorway[] {
  return seed.colorways.map((colorway, index) => ({
    id: `${seed.slug}-cw-${index + 1}`,
    name: colorway.name,
    colorCode: colorway.colorCode,
    sku: colorway.sku,
    priceOverride: colorway.amount ?? null,
    sizes: colorway.sizes.map(([size, stock]) => ({ size, stock })),
  }))
}

function toChecks(seed: SneakerSeed): PublishCheck[] {
  const stock = seedStock(seed)
  return [
    {
      label: "Tiene foto principal",
      state: seed.imageCount > 0 ? "ok" : "pending",
    },
    {
      label: "Al menos un color con tallas",
      state: seed.colorways.some((colorway) => colorway.sizes.length > 0)
        ? "ok"
        : "pending",
    },
    {
      label: stock > 0 ? `${stock} pares en stock` : "Sin pares en stock",
      state: stock > 0 ? "ok" : "pending",
    },
  ]
}

function toDraft(seed: SneakerSeed): AdminSneakerDraft {
  return {
    slug: seed.slug,
    name: seed.name,
    description: seed.description,
    brand: seed.brand,
    category: seed.category,
    gender: seed.gender,
    price: { amount: seed.amount, currency: seed.currency },
    releaseDate: seed.updatedAt,
    specs: seed.specs,
    usage: seed.usage,
    testimonialQuote: seed.testimonial?.quote ?? "",
    testimonialAuthor: seed.testimonial?.author ?? "",
    colorways: toColorways(seed),
    images: Array.from({ length: seed.imageCount }, (_, index) => ({
      id: `${seed.slug}-img-${index + 1}`,
      isPrimary: index === 0,
    })),
    status: seed.status,
    stock: seedStock(seed),
    updatedAt: seed.updatedAt,
    checks: toChecks(seed),
  }
}

const ROWS = CATALOG_SEEDS.map(toRow)

export async function listAdminSneakers(): Promise<AdminSneakerRow[]> {
  return ROWS
}

export async function getAdminStats(): Promise<AdminStats> {
  return {
    total: ROWS.length,
    published: ROWS.filter((row) => row.status === "active").length,
    drafts: ROWS.filter((row) => row.status === "draft").length,
    outOfStock: ROWS.filter((row) => row.stock === 0).length,
  }
}

export async function getAdminSneaker(
  slug: string
): Promise<AdminSneakerDraft | null> {
  const seed = CATALOG_SEEDS.find((item) => item.slug === slug)
  return seed ? toDraft(seed) : null
}

export async function listAdminSlugs(): Promise<string[]> {
  return CATALOG_SEEDS.map((seed) => seed.slug)
}

export async function listBrandOptions(): Promise<string[]> {
  return [...new Set(CATALOG_SEEDS.map((seed) => seed.brand))].sort()
}

export async function listCategoryOptions(): Promise<string[]> {
  return [...new Set(CATALOG_SEEDS.map((seed) => seed.category))].sort()
}
