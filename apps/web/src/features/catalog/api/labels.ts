import { Currency, Gender } from "@/lib/api/types"

export const GENDER_LABELS: Record<Gender, string> = {
  [Gender.MEN]: "Hombre",
  [Gender.WOMEN]: "Mujer",
  [Gender.UNISEX]: "Unisex",
  [Gender.KIDS]: "Niños",
}

export const GENDER_OPTIONS = Object.values(Gender).map((value) => ({
  value,
  label: GENDER_LABELS[value],
}))

export const CURRENCY_OPTIONS = Object.values(Currency)
