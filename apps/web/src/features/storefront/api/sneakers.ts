import type {
  CatalogFacets,
  CatalogPage,
  Colorway,
  SneakerDetail,
  SneakerImage,
  SneakerSummary,
} from "@/features/storefront/api/types"
import { CATALOG_SEEDS, type SneakerSeed } from "@/lib/catalog-sample"

function toColorways(seed: SneakerSeed): Colorway[] {
  return seed.colorways.map((colorway, index) => ({
    id: `${seed.slug}-cw-${index + 1}`,
    name: colorway.name,
    colorCode: colorway.colorCode,
    sku: colorway.sku,
    price: { amount: colorway.amount ?? seed.amount, currency: seed.currency },
    sizes: colorway.sizes.map(([size, stock]) => ({ size, stock })),
  }))
}

function toImages(seed: SneakerSeed): SneakerImage[] {
  return Array.from({ length: seed.imageCount }, (_, index) => ({
    id: `${seed.slug}-img-${index + 1}`,
    url: null,
    alt: `${seed.name} de ${seed.brand}, vista ${index + 1}`,
    isPrimary: index === 0,
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

function toDetail(seed: SneakerSeed): SneakerDetail {
  const colorways = toColorways(seed)
  const images = toImages(seed)
  const stock = availableStock(colorways)
  return {
    id: seed.slug,
    slug: seed.slug,
    name: seed.name,
    brand: seed.brand,
    category: seed.category,
    gender: seed.gender,
    reference: seed.reference,
    price: { amount: seed.amount, currency: seed.currency },
    colorCodes: colorways.map((colorway) => colorway.colorCode),
    sizeRange: sizeRange(colorways),
    badge: stock === 0 ? "sold-out" : seed.highlight,
    image: images[0] ?? null,
    description: seed.description,
    usage: seed.usage,
    specs: seed.specs,
    testimonial: seed.testimonial,
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

const PUBLISHED = CATALOG_SEEDS.filter((seed) => seed.status === "active").map(
  toDetail
)

export async function listSneakers(page = 1, size = 9): Promise<CatalogPage> {
  const start = (page - 1) * size
  return {
    items: PUBLISHED.slice(start, start + size).map(toSummary),
    total: PUBLISHED.length,
    page,
    size,
    pages: Math.max(1, Math.ceil(PUBLISHED.length / size)),
  }
}

export async function listFeatured(limit = 4): Promise<SneakerSummary[]> {
  return PUBLISHED.slice(0, limit).map(toSummary)
}

export async function listRelated(
  slug: string,
  limit = 4
): Promise<SneakerSummary[]> {
  return PUBLISHED.filter((detail) => detail.slug !== slug)
    .slice(0, limit)
    .map(toSummary)
}

export async function getSneakerBySlug(
  slug: string
): Promise<SneakerDetail | null> {
  return PUBLISHED.find((detail) => detail.slug === slug) ?? null
}

export async function listSlugs(): Promise<string[]> {
  return PUBLISHED.map((detail) => detail.slug)
}

export async function getFacets(): Promise<CatalogFacets> {
  const countBy = (pick: (detail: SneakerDetail) => string) => {
    const counts = new Map<string, number>()
    for (const detail of PUBLISHED) {
      const key = pick(detail)
      counts.set(key, (counts.get(key) ?? 0) + 1)
    }
    return [...counts.entries()]
      .map(([label, count]) => ({ value: label.toLowerCase(), label, count }))
      .sort((left, right) => right.count - left.count)
  }

  const sizes = new Set<string>()
  for (const detail of PUBLISHED) {
    for (const colorway of detail.colorways) {
      for (const variant of colorway.sizes) {
        sizes.add(variant.size)
      }
    }
  }

  return {
    brands: countBy((detail) => detail.brand),
    categories: countBy((detail) => detail.category),
    genders: countBy((detail) => detail.gender),
    sizes: [...sizes]
      .sort((left, right) => Number(left) - Number(right))
      .map((size) => ({ value: size, label: size, count: 0, available: true })),
    colors: [
      { value: "#1B4FC0", label: "Azul" },
      { value: "#FFFFFF", label: "Blanco" },
      { value: "#15161A", label: "Negro" },
      { value: "#9AA1AC", label: "Gris" },
      { value: "#D9C9AE", label: "Arena" },
      { value: "#3A2A1E", label: "Marrón" },
    ],
    currencies: ["USD", "CUP", "EUR"],
  }
}
