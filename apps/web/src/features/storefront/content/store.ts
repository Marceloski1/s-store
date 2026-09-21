export const STORE_NAME = "ALESA"

export const STORE_TAGLINE = "Cada paso es un gesto de cuidado y distinción"

export const STORE_INTRO =
  "Bienvenidos a ALESA, un espacio pensado para consentir cada uno de tus pasos. En nuestro catálogo descubrirás una selección de calzado deportivo, elegante y cómodo, diseñado para acompañarte en tu día a día."

export const STORE_HOURS = "9:00 – 17:00"

export const STORE_ADDRESSES = [
  {
    kind: "current",
    label: "Dirección actual",
    value: "Colón 13415, entre Unión y Acacia, Cerro, Reparto Martí, La Habana",
  },
  {
    kind: "upcoming",
    label: "Próximamente",
    value: "Jesús María 307, entre Picota y Curazao, Habana Vieja",
  },
] as const

// TODO(store): revisar los contactos de WhatsApp y la información de sneakers que se ofrece
export const WHATSAPP_CONTACTS = [
  { label: "+53 5608 1252", href: "https://wa.me/5356081252" },
  { label: "+53 5371 9152", href: "https://wa.me/5353719152" },
] as const

export const PRIMARY_WHATSAPP = WHATSAPP_CONTACTS[0]

export const SOCIAL_LINKS = [
  {
    name: "Instagram",
    label: "@somos_alesa",
    href: "https://instagram.com/somos_alesa",
  },
  // TODO(store): completar el usuario de Facebook y añadir el canal de YouTube cuando exista
  { name: "Facebook", label: "[USUARIO DE FACEBOOK]", href: null },
] as const

// TODO(store): revisar la información del proveedor
export const STORE_VALUES = [
  {
    title: "Calidad comprobada",
    detail: "Revisamos cada par antes de publicarlo en el catálogo.",
  },
  {
    title: "Estilo en cada modelo",
    detail: "Una selección propia, no un catálogo de almacén.",
  },
  {
    title: "Comodidad todo el día",
    detail: "Amortiguación y horma indicadas en cada ficha.",
  },
] as const

export const STORE_STYLES = [
  {
    slug: "deportivo",
    name: "Deportivo",
    detail: "Running, básquet y entrenamiento",
  },
  {
    slug: "elegante",
    name: "Elegante",
    detail: "Para la oficina y las ocasiones",
  },
  {
    slug: "diario",
    name: "Diario",
    detail: "Comodidad de la mañana a la noche",
  },
] as const

export const SEARCH_CRITERIA = [
  { prefix: "Filtrar por", label: "Marca", query: "?brand=nike" },
  { prefix: "Buscar por", label: "Referencia #", query: "?reference=ALS" },
  { prefix: "Ordenar por", label: "Precio", query: "?sort=price_asc" },
  {
    prefix: "Categoría",
    label: "Calzado deportivo",
    query: "?category=deportivo",
  },
] as const

export function whatsappLink(message: string): string {
  return `${PRIMARY_WHATSAPP.href}?text=${encodeURIComponent(message)}`
}
