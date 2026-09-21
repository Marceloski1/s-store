import type { ApiGender } from "@/lib/api/types"

export const GENDER_LABELS: Record<ApiGender, string> = {
  men: "Hombre",
  women: "Mujer",
  unisex: "Unisex",
  kids: "Niños",
}

export const GENDER_OPTIONS = Object.entries(GENDER_LABELS).map(
  ([value, label]) => ({ value: value as ApiGender, label })
)

export const CURRENCY_OPTIONS = ["USD", "CUP", "EUR"] as const
