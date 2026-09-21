import { useState } from "react"

import type { Colorway, SizeVariant } from "@/features/storefront/api/types"

type SneakerSelection = {
  colorway: Colorway | null
  size: SizeVariant | null
  selectColorway: (colorwayId: string) => void
  selectSize: (size: string) => void
}

export function useSneakerSelection(colorways: Colorway[]): SneakerSelection {
  const [colorwayId, setColorwayId] = useState<string | null>(
    colorways[0]?.id ?? null
  )
  const [size, setSize] = useState<string | null>(null)

  const colorway =
    colorways.find((item) => item.id === colorwayId) ?? colorways[0] ?? null
  const selectedSize =
    colorway?.sizes.find(
      (variant) => variant.size === size && variant.stock > 0
    ) ?? null

  return {
    colorway,
    size: selectedSize,
    selectColorway: (nextId) => {
      setColorwayId(nextId)
      setSize(null)
    },
    selectSize: setSize,
  }
}
