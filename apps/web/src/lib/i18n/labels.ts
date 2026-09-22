import { Role, SneakerStatus } from "@/lib/api/types"

export const SNEAKER_STATUS_LABELS: Record<SneakerStatus, string> = {
  [SneakerStatus.DRAFT]: "Borrador",
  [SneakerStatus.ACTIVE]: "Publicado",
  [SneakerStatus.ARCHIVED]: "Archivado",
}

export const ROLE_LABELS: Record<Role, string> = {
  [Role.ADMIN]: "Administrador",
  [Role.SUPER_ADMIN]: "Superadministrador",
}

export const FIELD_LABELS: Partial<Record<string, string>> = {
  name: "nombre",
  slug: "slug",
  description: "descripción",
  reference: "referencia",
  brand_id: "marca",
  category_id: "categoría",
  gender: "género",
  price: "precio",
  price_override: "precio propio",
  currency: "moneda",
  release_date: "fecha de lanzamiento",
  usage: "recomendación de uso",
  "specs.material": "material",
  "specs.technology": "tecnología",
  "specs.weight": "peso",
  "specs.cushioning": "amortiguación",
  material: "material",
  technology: "tecnología",
  weight: "peso",
  cushioning: "amortiguación",
  "testimonial.quote": "testimonio",
  "testimonial.author": "autor del testimonio",
  "testimonial quote": "testimonio",
  "testimonial author": "autor del testimonio",
  color_code: "color",
  sku: "SKU",
  stock: "stock",
  size: "talla",
  alt: "texto alternativo",
  file: "archivo",
  image_ids: "orden de fotos",
  email: "correo",
  password: "contraseña",
  is_active: "estado",
  page: "página",
  q: "búsqueda",
  min_price: "precio mínimo",
  max_price: "precio máximo",
  shoe_size: "talla",
  color: "color",
  sort: "orden",
  status: "estado",
}

export function fieldLabel(field: string | number | undefined): string {
  const key = String(field ?? "")
  return FIELD_LABELS[key] ?? FIELD_LABELS[key.split(".")[0] ?? ""] ?? key
}
