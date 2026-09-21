import { cn } from "cn"

import type { SizeVariant } from "@/features/storefront/api/types"

type SizePickerProps = {
  sizes: SizeVariant[]
  selected: string | null
  onSelect: (size: string) => void
}

export function SizePicker({ sizes, selected, onSelect }: SizePickerProps) {
  return (
    <div className="grid grid-cols-5 gap-2">
      {sizes.map((variant) => {
        const soldOut = variant.stock === 0
        const active = variant.size === selected
        return (
          <button
            key={variant.size}
            type="button"
            disabled={soldOut}
            aria-pressed={active}
            onClick={() => onSelect(variant.size)}
            className={cn(
              "h-13 text-sm font-bold outline-none focus-visible:ring-1 focus-visible:ring-ring",
              soldOut &&
                "border border-dashed border-border bg-muted text-muted-foreground line-through",
              !soldOut &&
                active &&
                "border-[1.5px] border-primary bg-primary text-primary-foreground",
              !soldOut &&
                !active &&
                "border border-input bg-background text-foreground hover:border-primary"
            )}
          >
            {variant.size}
          </button>
        )
      })}
    </div>
  )
}
