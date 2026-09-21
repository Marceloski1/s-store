import { useState } from "react"

import { ColorwayPicker } from "@/features/storefront/components/colorway-picker"
import { SizePicker } from "@/features/storefront/components/size-picker"
import { useSneakerSelection } from "@/features/storefront/hooks/use-sneaker-selection"
import {
  formatMoney,
  type SneakerDetail,
} from "@/features/storefront/api/types"
import { whatsappLink } from "@/features/storefront/content/store"

type SneakerPurchasePanelProps = {
  sneaker: SneakerDetail
}

export function SneakerPurchasePanel({ sneaker }: SneakerPurchasePanelProps) {
  const { colorway, size, selectColorway, selectSize } = useSneakerSelection(
    sneaker.colorways
  )
  const [copied, setCopied] = useState(false)

  const price = colorway?.price ?? sneaker.price
  const reference = colorway?.sku ?? sneaker.reference
  const stockLine = size
    ? `Talla ${size.size} disponible — quedan ${size.stock} pares`
    : "Elige una talla disponible para consultar"

  const message = [
    `Hola ALESA, me interesa el modelo ${sneaker.name}`,
    colorway ? ` en ${colorway.name}` : "",
    size ? ` talla ${size.size}` : "",
    ` (ref. ${reference}).`,
  ].join("")

  const share = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <span className="text-[11px] font-extrabold tracking-[0.18em] text-primary uppercase">
        {sneaker.brand} · {sneaker.category}
      </span>
      <h1 className="font-display text-4xl font-extrabold tracking-tight text-foreground uppercase sm:text-5xl">
        {sneaker.name}
      </h1>
      <span className="text-[13px] font-semibold text-muted-foreground">
        Código de referencia: {reference} · {sneaker.gender}
      </span>
      <span className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
        {formatMoney(price)}
      </span>

      {colorway && (
        <div className="flex flex-col gap-3 border-t border-border pt-5">
          <span className="text-[11px] font-extrabold tracking-[0.14em] text-foreground uppercase">
            Color:{" "}
            <span className="text-muted-foreground">{colorway.name}</span>
          </span>
          <ColorwayPicker
            colorways={sneaker.colorways}
            selectedId={colorway.id}
            onSelect={selectColorway}
          />
        </div>
      )}

      {colorway && (
        <div className="flex flex-col gap-3 border-t border-border pt-5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-extrabold tracking-[0.14em] text-foreground uppercase">
              Talla (EU)
            </span>
            <a
              href="#guia-de-tallas"
              className="text-xs font-bold text-primary underline"
            >
              Guía de tallas
            </a>
          </div>
          <SizePicker
            sizes={colorway.sizes}
            selected={size?.size ?? null}
            onSelect={selectSize}
          />
          <span className="text-[13px] font-semibold text-primary">
            {stockLine}
          </span>
        </div>
      )}

      <div className="flex flex-col gap-2.5 pt-1">
        <a
          href={whatsappLink(message)}
          className="flex h-14 items-center justify-center gap-3 bg-primary text-sm font-extrabold tracking-[0.08em] text-primary-foreground uppercase hover:bg-primary/90"
        >
          <svg
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.9"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M21 11.5a8.4 8.4 0 0 1-12.4 7.4L3.5 20.5l1.7-5A8.4 8.4 0 1 1 21 11.5Z" />
            <path d="M8.9 9.3c0 3 2.4 5.4 5.4 5.4" />
          </svg>
          Consultar este modelo
        </a>
        <button
          type="button"
          onClick={share}
          className="flex h-13 items-center justify-center gap-2.5 border-[1.5px] border-foreground bg-background text-[13px] font-extrabold tracking-[0.08em] text-foreground uppercase hover:bg-muted"
        >
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.9"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M12 16V4m0 0L8 8m4-4 4 4" />
            <path d="M5 15v3.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V15" />
          </svg>
          {copied ? "Enlace copiado" : "Compartir el modelo"}
        </button>
      </div>

      {sneaker.usage && (
        <div className="flex flex-col gap-1.5 border-l-[3px] border-primary bg-muted p-4">
          <span className="text-[11px] font-extrabold tracking-[0.14em] text-primary uppercase">
            Recomendación de uso
          </span>
          <span className="text-sm leading-relaxed text-foreground">
            {sneaker.usage}
          </span>
        </div>
      )}
    </div>
  )
}
