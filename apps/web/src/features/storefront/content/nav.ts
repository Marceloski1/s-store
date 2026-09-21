export enum StorefrontSection {
  CATALOG = "CATALOG",
  SPORT = "SPORT",
  ELEGANT = "ELEGANT",
  DAILY = "DAILY",
  CONTACT = "CONTACT",
}

export const STOREFRONT_SECTION_LABELS: Record<StorefrontSection, string> = {
  [StorefrontSection.CATALOG]: "Catálogo",
  [StorefrontSection.SPORT]: "Deportivo",
  [StorefrontSection.ELEGANT]: "Elegante",
  [StorefrontSection.DAILY]: "Diario",
  [StorefrontSection.CONTACT]: "Contacto",
}

const SECTION_CATEGORY_SLUGS: Partial<Record<StorefrontSection, string>> = {
  [StorefrontSection.SPORT]: "deportivo",
  [StorefrontSection.ELEGANT]: "elegante",
  [StorefrontSection.DAILY]: "diario",
}

function hrefFor(section: StorefrontSection): string {
  if (section === StorefrontSection.CONTACT) return "/#contacto"
  const category = SECTION_CATEGORY_SLUGS[section]
  return category ? `/sneakers?category=${category}` : "/sneakers"
}

export function sectionForCategories(categories: string[]): StorefrontSection {
  if (categories.length !== 1) return StorefrontSection.CATALOG
  const match = Object.values(StorefrontSection).find(
    (section) => SECTION_CATEGORY_SLUGS[section] === categories[0]
  )
  return match ?? StorefrontSection.CATALOG
}

export const STOREFRONT_NAV = Object.values(StorefrontSection).map(
  (section) => ({
    section,
    label: STOREFRONT_SECTION_LABELS[section],
    href: hrefFor(section),
  })
)
