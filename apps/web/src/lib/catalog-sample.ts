export type SneakerStatus = "draft" | "active" | "archived"

export type SizeEntry = [string, number]

export type ColorwaySeed = {
  name: string
  colorCode: string
  sku: string
  amount?: string
  sizes: SizeEntry[]
}

export type SpecSeed = {
  material: string
  technology: string
  weight: string
  cushioning: string
}

export type TestimonialSeed = {
  quote: string
  author: string
}

export type SneakerSeed = {
  slug: string
  name: string
  brand: string
  category: string
  gender: string
  reference: string
  amount: string
  currency: string
  description: string
  usage: string
  specs: SpecSeed
  testimonial: TestimonialSeed | null
  highlight: "new" | "last-sizes" | null
  status: SneakerStatus
  updatedAt: string
  imageCount: number
  colorways: ColorwaySeed[]
}

const FULL_RUN: SizeEntry[] = [
  ["38", 2],
  ["39", 4],
  ["40", 6],
  ["41", 3],
  ["42", 5],
  ["42.5", 1],
  ["43", 0],
  ["44", 2],
  ["45", 0],
]

const MID_RUN: SizeEntry[] = [
  ["40", 3],
  ["41", 2],
  ["42", 4],
  ["43", 1],
  ["44", 0],
  ["45", 2],
]

const SMALL_RUN: SizeEntry[] = [
  ["36", 1],
  ["37", 2],
  ["38", 3],
  ["39", 2],
  ["40", 0],
]

const EMPTY_RUN: SizeEntry[] = [
  ["39", 0],
  ["40", 0],
  ["41", 0],
  ["42", 0],
]

// TODO(001): sustituir este catálogo de ejemplo por los gateways tipados contra la API
export const CATALOG_SEEDS: SneakerSeed[] = [
  {
    slug: "runner-pro-2",
    name: "Runner Pro 2",
    brand: "Nike",
    category: "Deportivo",
    gender: "Unisex",
    reference: "ALS-RP2-001",
    amount: "145.00",
    currency: "USD",
    description:
      "Un modelo pensado para quien camina mucho y no quiere elegir entre comodidad y estilo. La malla mantiene el pie fresco y la entresuela absorbe el impacto del asfalto sin perder respuesta.",
    usage:
      "Ideal para running diario y jornadas largas de pie. Combina con ropa deportiva o vaquero recto.",
    specs: {
      material: "Malla técnica transpirable con refuerzos sintéticos",
      technology: "Placa de propulsión y suela de agarre multidirección",
      weight: "268 g en talla EU 42",
      cushioning: "Espuma de doble densidad con retorno de energía",
    },
    testimonial: {
      quote:
        "Camino más de dos horas al día por La Habana Vieja y es el primer par con el que llego a casa sin dolor.",
      author: "Yoandy P. · compró la talla 42",
    },
    highlight: "new",
    status: "active",
    updatedAt: "2026-09-20",
    imageCount: 4,
    colorways: [
      {
        name: "Azul cobalto / Blanco",
        colorCode: "#1B4FC0",
        sku: "ALS-RP2-001",
        sizes: FULL_RUN,
      },
      {
        name: "Negro total",
        colorCode: "#15161A",
        sku: "ALS-RP2-002",
        sizes: MID_RUN,
      },
      {
        name: "Blanco hueso",
        colorCode: "#F2F1ED",
        sku: "ALS-RP2-003",
        amount: "139.00",
        sizes: SMALL_RUN,
      },
    ],
  },
  {
    slug: "air-step-max",
    name: "Air Step Max",
    brand: "Nike",
    category: "Deportivo",
    gender: "Hombre",
    reference: "ALS-ASM-031",
    amount: "168.00",
    currency: "USD",
    description:
      "Silueta alta con cámara de aire visible. Pensado para quien quiere presencia sin renunciar a la amortiguación.",
    usage: "Para el día a día urbano y entrenamientos de baja intensidad.",
    specs: {
      material: "Piel sintética con paneles de malla",
      technology: "Cámara de aire visible en el talón",
      weight: "312 g en talla EU 42",
      cushioning: "Unidad de aire más espuma de rebote",
    },
    testimonial: null,
    highlight: null,
    status: "active",
    updatedAt: "2026-09-19",
    imageCount: 3,
    colorways: [
      {
        name: "Negro / Gris",
        colorCode: "#15161A",
        sku: "ALS-ASM-031",
        sizes: MID_RUN,
      },
      {
        name: "Gris hielo",
        colorCode: "#9AA1AC",
        sku: "ALS-ASM-032",
        sizes: MID_RUN,
      },
    ],
  },
  {
    slug: "trail-light-4",
    name: "Trail Light 4",
    brand: "New Balance",
    category: "Deportivo",
    gender: "Unisex",
    reference: "ALS-TL4-022",
    amount: "132.00",
    currency: "USD",
    description:
      "Suela con tacos profundos y refuerzo en la puntera para terreno irregular, sin el peso de una bota.",
    usage: "Senderismo ligero y caminatas largas fuera del asfalto.",
    specs: {
      material: "Malla reforzada con tratamiento repelente al agua",
      technology: "Suela de tacos profundos y placa antipiedras",
      weight: "289 g en talla EU 42",
      cushioning: "Espuma de media densidad con soporte de arco",
    },
    testimonial: {
      quote:
        "Los usé en Viñales tres días seguidos y no me resbalé ni una vez.",
      author: "Claudia M. · compró la talla 39",
    },
    highlight: null,
    status: "active",
    updatedAt: "2026-09-17",
    imageCount: 3,
    colorways: [
      {
        name: "Azul profundo",
        colorCode: "#1B4FC0",
        sku: "ALS-TL4-022",
        sizes: MID_RUN,
      },
      {
        name: "Arena",
        colorCode: "#D9C9AE",
        sku: "ALS-TL4-023",
        sizes: SMALL_RUN,
      },
      {
        name: "Negro",
        colorCode: "#15161A",
        sku: "ALS-TL4-024",
        sizes: MID_RUN,
      },
    ],
  },
  {
    slug: "court-classic-70",
    name: "Court Classic 70",
    brand: "Converse",
    category: "Diario",
    gender: "Unisex",
    reference: "ALS-CC7-014",
    amount: "89.00",
    currency: "USD",
    description:
      "El clásico de lona que combina con todo. Corte bajo, suela de goma vulcanizada y nada más.",
    usage: "Para el día a día. Queda bien con vaquero, short o vestido.",
    specs: {
      material: "Lona de algodón con puntera de goma",
      technology: "Suela vulcanizada cosida",
      weight: "244 g en talla EU 42",
      cushioning: "Plantilla extraíble acolchada",
    },
    testimonial: null,
    highlight: null,
    status: "draft",
    updatedAt: "2026-09-17",
    imageCount: 0,
    colorways: [
      {
        name: "Blanco",
        colorCode: "#FFFFFF",
        sku: "ALS-CC7-014",
        sizes: SMALL_RUN,
      },
      {
        name: "Negro",
        colorCode: "#15161A",
        sku: "ALS-CC7-015",
        sizes: MID_RUN,
      },
    ],
  },
  {
    slug: "urban-low",
    name: "Urban Low",
    brand: "Adidas",
    category: "Diario",
    gender: "Unisex",
    reference: "ALS-UBL-009",
    amount: "118.00",
    currency: "USD",
    description:
      "Corte bajo de piel con tres bandas perforadas. Un par que aguanta el uso diario y sigue viéndose nuevo.",
    usage: "Diario y salidas informales. Fácil de limpiar.",
    specs: {
      material: "Piel lisa con forro textil",
      technology: "Suela de goma con dibujo en espiga",
      weight: "296 g en talla EU 42",
      cushioning: "Entresuela de EVA moldeada",
    },
    testimonial: null,
    highlight: "last-sizes",
    status: "active",
    updatedAt: "2026-09-15",
    imageCount: 3,
    colorways: [
      {
        name: "Blanco / Verde",
        colorCode: "#FFFFFF",
        sku: "ALS-UBL-009",
        sizes: SMALL_RUN,
      },
      {
        name: "Azul marino",
        colorCode: "#1B4FC0",
        sku: "ALS-UBL-010",
        sizes: MID_RUN,
      },
      {
        name: "Gris",
        colorCode: "#9AA1AC",
        sku: "ALS-UBL-011",
        sizes: SMALL_RUN,
      },
      {
        name: "Negro",
        colorCode: "#15161A",
        sku: "ALS-UBL-012",
        sizes: MID_RUN,
      },
    ],
  },
  {
    slug: "street-force",
    name: "Street Force",
    brand: "Puma",
    category: "Deportivo",
    gender: "Hombre",
    reference: "ALS-STF-017",
    amount: "96.00",
    currency: "USD",
    description:
      "Silueta ancha y sujeción firme en el tobillo. Pensado para entrenar en pista y calle.",
    usage: "Entrenamiento en gimnasio y cancha.",
    specs: {
      material: "Malla técnica con refuerzos termosellados",
      technology: "Contrafuerte rígido y suela plana de agarre",
      weight: "305 g en talla EU 42",
      cushioning: "Espuma firme de soporte lateral",
    },
    testimonial: null,
    highlight: null,
    status: "active",
    updatedAt: "2026-09-12",
    imageCount: 3,
    colorways: [
      {
        name: "Negro / Rojo",
        colorCode: "#15161A",
        sku: "ALS-STF-017",
        sizes: MID_RUN,
      },
      {
        name: "Azul eléctrico",
        colorCode: "#1B4FC0",
        sku: "ALS-STF-018",
        sizes: MID_RUN,
      },
      {
        name: "Gris grafito",
        colorCode: "#9AA1AC",
        sku: "ALS-STF-019",
        sizes: MID_RUN,
      },
    ],
  },
  {
    slug: "daily-canvas",
    name: "Daily Canvas",
    brand: "Vans",
    category: "Diario",
    gender: "Unisex",
    reference: "ALS-DCV-005",
    amount: "74.00",
    currency: "USD",
    description:
      "Lona resistente, suela de gofre y una horma que se adapta en dos usos.",
    usage: "Para caminar por la ciudad y usar a diario.",
    specs: {
      material: "Lona doble con refuerzo en talón",
      technology: "Suela de gofre de goma",
      weight: "238 g en talla EU 42",
      cushioning: "Plantilla acolchada",
    },
    testimonial: null,
    highlight: null,
    status: "draft",
    updatedAt: "2026-09-10",
    imageCount: 2,
    colorways: [
      {
        name: "Negro",
        colorCode: "#15161A",
        sku: "ALS-DCV-005",
        sizes: SMALL_RUN,
      },
      {
        name: "Arena",
        colorCode: "#D9C9AE",
        sku: "ALS-DCV-006",
        sizes: MID_RUN,
      },
    ],
  },
  {
    slug: "elegance-derby",
    name: "Elegance Derby",
    brand: "ALESA Select",
    category: "Elegante",
    gender: "Hombre",
    reference: "ALS-EDB-002",
    amount: "135.00",
    currency: "USD",
    description:
      "Derby de piel con costura Blake y suela fina. El par para la oficina, una boda o una cena.",
    usage: "Ocasiones formales y oficina. Combina con traje o chino.",
    specs: {
      material: "Piel de becerro con forro de piel",
      technology: "Construcción Blake cosida",
      weight: "372 g en talla EU 42",
      cushioning: "Plantilla de piel sobre corcho",
    },
    testimonial: {
      quote:
        "Los estrené en una boda de ocho horas y no me sacaron una ampolla.",
      author: "Reinier A. · compró la talla 43",
    },
    highlight: null,
    status: "draft",
    updatedAt: "2026-09-06",
    imageCount: 3,
    colorways: [
      {
        name: "Marrón cuero",
        colorCode: "#3A2A1E",
        sku: "ALS-EDB-002",
        sizes: EMPTY_RUN,
      },
      {
        name: "Negro",
        colorCode: "#15161A",
        sku: "ALS-EDB-003",
        sizes: EMPTY_RUN,
      },
    ],
  },
  {
    slug: "motion-knit-w",
    name: "Motion Knit W",
    brand: "Adidas",
    category: "Deportivo",
    gender: "Mujer",
    reference: "ALS-MKW-028",
    amount: "124.00",
    currency: "USD",
    description:
      "Tejido de punto elástico que se ajusta como un calcetín. Horma femenina más estrecha en el talón.",
    usage: "Running suave, clases dirigidas y uso diario.",
    specs: {
      material: "Tejido de punto elástico sin costuras",
      technology: "Refuerzo interno en el arco",
      weight: "232 g en talla EU 39",
      cushioning: "Espuma ligera de retorno alto",
    },
    testimonial: null,
    highlight: null,
    status: "archived",
    updatedAt: "2026-09-02",
    imageCount: 3,
    colorways: [
      {
        name: "Blanco",
        colorCode: "#FFFFFF",
        sku: "ALS-MKW-028",
        sizes: EMPTY_RUN,
      },
      {
        name: "Azul cielo",
        colorCode: "#1B4FC0",
        sku: "ALS-MKW-029",
        sizes: EMPTY_RUN,
      },
      {
        name: "Arena",
        colorCode: "#D9C9AE",
        sku: "ALS-MKW-030",
        sizes: EMPTY_RUN,
      },
    ],
  },
]

export function seedStock(seed: SneakerSeed): number {
  return seed.colorways.reduce(
    (total, colorway) =>
      total + colorway.sizes.reduce((sum, [, stock]) => sum + stock, 0),
    0
  )
}
