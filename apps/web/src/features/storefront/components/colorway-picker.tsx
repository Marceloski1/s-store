import { cn } from "cn"

import type { Colorway } from "@/features/storefront/api/types"

type ColorwayPickerProps = {
  // TODO(003): revisar este patrón de props del selector de colores
  colorways: Colorway[]
  selectedId: string | null
  onSelect: (colorwayId: string) => void
}

export function ColorwayPicker({
  colorways,
  selectedId,
  onSelect,
}: ColorwayPickerProps) {
  return (
    <div className="flex flex-wrap gap-3">
      {colorways.map((colorway) => (
        <button
          key={colorway.id}
          type="button"
          aria-label={colorway.name}
          aria-pressed={colorway.id === selectedId}
          onClick={() => onSelect(colorway.id)}
          style={{ backgroundColor: colorway.colorCode }}
          className={cn(
            "size-14 border outline-none focus-visible:ring-1 focus-visible:ring-ring",
            colorway.id === selectedId
              ? "border-[3px] border-primary"
              : "border-input"
          )}
        />
      ))}
    </div>
  )
}
