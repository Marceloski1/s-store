import { useState } from "react"

import { Form } from "@workspace/ui/components/form"

import { colorwayFormSchema } from "@/features/admin/api/schemas"

import {
  colorwayStock,
  colorwayToInput,
  formatSize,
  type AdminMoney,
  type ColorwayInput,
} from "@/features/admin/api/types"
import {
  fieldClass,
  invalidClass,
  sectionClass,
  smallLabelClass,
} from "@/features/admin/components/editor-styles"
import { ColorwayField } from "@/features/admin/components/form-fields"
import type { ApiColorway } from "@/lib/api/types"

type ColorwaysSectionProps = {
  colorways: ApiColorway[]
  basePrice: AdminMoney
  totalStock: number
  disabled: boolean
  onAdd: (input: ColorwayInput) => Promise<unknown>
  onUpdate: (colorwayId: string, input: ColorwayInput) => Promise<unknown>
  onRemove: (colorwayId: string) => Promise<unknown>
  onSetStock: (colorwayId: string, size: string, stock: number) => void
  onRemoveSize: (colorwayId: string, size: string) => void
}

const EMPTY_COLORWAY: ColorwayInput = {
  name: "",
  colorCode: "#1B4FC0",
  sku: "",
  priceOverride: "",
}

function PlusIcon({ size = 14 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.3"
      strokeLinecap="round"
      aria-hidden="true"
    >
      <path d="M12 5v14M5 12h14" />
    </svg>
  )
}

export function ColorwaysSection({
  colorways,
  basePrice,
  totalStock,
  disabled,
  onAdd,
  onUpdate,
  onRemove,
  onSetStock,
  onRemoveSize,
}: ColorwaysSectionProps) {
  const [expandedId, setExpandedId] = useState<string | null>(
    colorways[0]?.id ?? null
  )
  const [newColorway, setNewColorway] = useState<ColorwayInput | null>(null)

  const expanded =
    colorways.find((colorway) => colorway.id === expandedId) ?? colorways[0]
  const others = colorways.filter((colorway) => colorway !== expanded)

  async function submitNewColorway(input: ColorwayInput) {
    const result = await onAdd(input)
    if (result) setNewColorway(null)
  }

  return (
    <section className={sectionClass}>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-6 py-4">
        <div className="flex items-baseline gap-2.5">
          <h2 className="text-[17px] font-extrabold">Colores y tallas</h2>
          <span className="text-[13px] text-muted-foreground">
            {colorways.length} colores · {totalStock} pares en total
          </span>
        </div>
        <button
          type="button"
          disabled={disabled}
          onClick={() => setNewColorway(EMPTY_COLORWAY)}
          className="flex h-10 items-center gap-2 border border-primary px-3.5 text-[11px] font-extrabold tracking-[0.06em] text-primary uppercase hover:bg-accent disabled:opacity-60"
        >
          <PlusIcon />
          Añadir color
        </button>
      </div>

      <div className="flex flex-col gap-3.5 px-6 py-5">
        {newColorway && (
          <ColorwayForm
            initial={newColorway}
            basePrice={basePrice}
            disabled={disabled}
            onSubmit={submitNewColorway}
            onCancel={() => setNewColorway(null)}
          />
        )}

        {colorways.length === 0 && !newColorway && (
          <p className="border border-dashed border-warning bg-warning/10 p-3 text-[13px] font-semibold text-warning">
            Este modelo todavía no tiene colores. Añade al menos uno con tallas
            para poder publicarlo.
          </p>
        )}

        {expanded && (
          <ColorwayCard
            key={`${expanded.id}-${expanded.name}-${expanded.sku}-${expanded.color_code}-${expanded.price_override?.amount ?? ""}`}
            colorway={expanded}
            basePrice={basePrice}
            disabled={disabled}
            onUpdate={(input) => onUpdate(expanded.id, input)}
            onRemove={() => onRemove(expanded.id)}
            onDuplicate={() =>
              setNewColorway({
                ...colorwayToInput(expanded),
                name: `${expanded.name} (copia)`,
                sku: `${expanded.sku}-2`,
              })
            }
            onSetStock={(size, stock) => onSetStock(expanded.id, size, stock)}
            onRemoveSize={(size) => onRemoveSize(expanded.id, size)}
          />
        )}

        {others.map((colorway) => (
          <div
            key={colorway.id}
            className="flex flex-wrap items-center gap-3.5 border border-border bg-card p-4"
          >
            <span
              className="size-9 shrink-0 border border-input"
              style={{ backgroundColor: colorway.color_code }}
              aria-hidden="true"
            />
            <div className="flex min-w-0 grow flex-col gap-0.5">
              <span className="text-sm font-bold">{colorway.name}</span>
              <span className="text-xs text-muted-foreground">
                {colorway.sku} · {colorway.sizes.length} tallas ·{" "}
                {colorwayStock(colorway)} pares ·{" "}
                {colorway.price_override
                  ? `${colorway.price_override.amount.replace(".", ",")} ${basePrice.currency} propio`
                  : "precio heredado"}
              </span>
            </div>
            <button
              type="button"
              onClick={() => setExpandedId(colorway.id)}
              className="h-10 border border-input px-3.5 text-[11px] font-extrabold tracking-[0.06em] uppercase hover:bg-muted"
            >
              Editar tallas
            </button>
          </div>
        ))}
      </div>
    </section>
  )
}

type ColorwayFieldsProps = {
  idPrefix: string
  basePrice: AdminMoney
  onCommit?: () => void
}

function ColorwayFields({
  idPrefix,
  basePrice,
  onCommit,
}: ColorwayFieldsProps) {
  return (
    <>
      <ColorwayField
        name="colorCode"
        id={`${idPrefix}-color`}
        label="Color"
        labelClassName={smallLabelClass}
        render={({ field, control }) => (
          <input
            {...control}
            {...field}
            type="color"
            value={field.value.toLowerCase()}
            onChange={(event) =>
              field.onChange(event.target.value.toUpperCase())
            }
            onBlur={() => {
              field.onBlur()
              onCommit?.()
            }}
            className="h-11 w-14 cursor-pointer border border-input bg-background p-1"
          />
        )}
      />
      <ColorwayField
        name="name"
        id={`${idPrefix}-name`}
        label="Nombre del color"
        labelClassName={smallLabelClass}
        render={({ field, fieldState, control }) => (
          <input
            {...control}
            {...field}
            type="text"
            onBlur={() => {
              field.onBlur()
              onCommit?.()
            }}
            className={invalidClass(fieldClass, fieldState.invalid)}
          />
        )}
      />
      <ColorwayField
        name="sku"
        id={`${idPrefix}-sku`}
        label="SKU (único)"
        labelClassName={smallLabelClass}
        render={({ field, fieldState, control }) => (
          <input
            {...control}
            {...field}
            type="text"
            onBlur={() => {
              field.onBlur()
              onCommit?.()
            }}
            className={invalidClass(
              `${fieldClass} uppercase`,
              fieldState.invalid
            )}
          />
        )}
      />
      <ColorwayField
        name="priceOverride"
        id={`${idPrefix}-price`}
        label="Precio propio"
        labelClassName={smallLabelClass}
        render={({ field, fieldState, control }) => (
          <input
            {...control}
            {...field}
            type="text"
            inputMode="decimal"
            placeholder={`${basePrice.amount} heredado`}
            onBlur={() => {
              field.onBlur()
              onCommit?.()
            }}
            className={invalidClass(fieldClass, fieldState.invalid)}
          />
        )}
      />
    </>
  )
}

type ColorwayFormProps = {
  initial: ColorwayInput
  basePrice: AdminMoney
  disabled: boolean
  onSubmit: (input: ColorwayInput) => Promise<void>
  onCancel: () => void
}

function ColorwayForm({
  initial,
  basePrice,
  disabled,
  onSubmit,
  onCancel,
}: ColorwayFormProps) {
  return (
    <Form
      schema={colorwayFormSchema}
      defaultValues={initial}
      disabled={disabled}
      onSubmit={onSubmit}
      className="border border-primary bg-accent/40"
    >
      <div className="grid items-start gap-3.5 p-4 sm:grid-cols-[56px_1.3fr_1fr_1fr_auto]">
        <ColorwayFields idPrefix="new-cw" basePrice={basePrice} />
        <div className="flex gap-1.5 sm:pt-[22px]">
          <button
            type="submit"
            disabled={disabled}
            className="h-11 bg-primary px-4 text-[11px] font-extrabold tracking-[0.06em] text-primary-foreground uppercase hover:bg-primary/90 disabled:opacity-60"
          >
            Añadir
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="h-11 border border-input bg-card px-3 text-[11px] font-extrabold tracking-[0.06em] uppercase hover:bg-muted"
          >
            Cancelar
          </button>
        </div>
      </div>
    </Form>
  )
}

type ColorwayCardProps = {
  colorway: ApiColorway
  basePrice: AdminMoney
  disabled: boolean
  onUpdate: (input: ColorwayInput) => Promise<unknown>
  onRemove: () => Promise<unknown>
  onDuplicate: () => void
  onSetStock: (size: string, stock: number) => void
  onRemoveSize: (size: string) => void
}

function isSameColorway(left: ColorwayInput, right: ColorwayInput): boolean {
  return (
    left.name.trim() === right.name.trim() &&
    left.colorCode.toUpperCase() === right.colorCode.toUpperCase() &&
    left.sku.trim().toUpperCase() === right.sku.trim().toUpperCase() &&
    left.priceOverride.trim() === right.priceOverride.trim()
  )
}

function ColorwayCard({
  colorway,
  basePrice,
  disabled,
  onUpdate,
  onRemove,
  onDuplicate,
  onSetStock,
  onRemoveSize,
}: ColorwayCardProps) {
  const saved = colorwayToInput(colorway)
  const [newSize, setNewSize] = useState<string | null>(null)

  async function commit(input: ColorwayInput) {
    if (!isSameColorway(input, saved)) await onUpdate(input)
  }

  function submitNewSize() {
    if (newSize === null) return
    const size = newSize.trim().replace(",", ".")
    if (size === "" || Number.isNaN(Number(size))) return
    onSetStock(size, 0)
    setNewSize(null)
  }

  return (
    <div className="border border-input bg-muted/40">
      <Form
        schema={colorwayFormSchema}
        defaultValues={saved}
        disabled={disabled}
        onSubmit={commit}
        className="grid items-start gap-3.5 p-4 sm:grid-cols-[56px_1.3fr_1fr_1fr_84px]"
      >
        {(form) => (
          <>
            <ColorwayFields
              idPrefix={`cw-${colorway.id}`}
              basePrice={basePrice}
              onCommit={() => void form.handleSubmit(commit)()}
            />
            <div className="flex justify-end gap-1.5 sm:pt-[22px]">
              <button
                type="button"
                aria-label="Duplicar este color"
                disabled={disabled}
                onClick={onDuplicate}
                className="flex h-11 w-9 items-center justify-center border border-input bg-card hover:bg-muted disabled:opacity-60"
              >
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <rect x="8.5" y="8.5" width="11" height="11" rx="1.5" />
                  <path d="M15.5 5.5H6A1.5 1.5 0 0 0 4.5 7v9.5" />
                </svg>
              </button>
              <button
                type="button"
                aria-label="Eliminar este color"
                disabled={disabled}
                onClick={() => {
                  if (
                    window.confirm(`¿Eliminar el color «${colorway.name}»?`)
                  ) {
                    void onRemove()
                  }
                }}
                className="flex h-11 w-9 items-center justify-center border border-input bg-card text-destructive hover:bg-muted disabled:opacity-60"
              >
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M4 7h16M9.5 7V4.5h5V7M6.5 7l1 13h9l1-13" />
                </svg>
              </button>
            </div>
          </>
        )}
      </Form>

      <div className="flex flex-col gap-3 border-t border-dashed border-input p-4">
        <span className="text-[10px] font-extrabold tracking-[0.12em] text-muted-foreground uppercase">
          Stock por talla (EU)
        </span>
        {colorway.sizes.length > 0 && (
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-6 lg:grid-cols-9">
            {colorway.sizes.map((variant) => {
              const inputId = `size-${colorway.id}-${variant.size}`
              return (
                <div key={variant.size} className="flex flex-col gap-1">
                  <div className="flex items-center justify-center gap-1">
                    <label
                      htmlFor={inputId}
                      className="text-center text-xs font-extrabold"
                    >
                      {formatSize(variant.size)}
                    </label>
                    <button
                      type="button"
                      aria-label={`Quitar la talla ${formatSize(variant.size)}`}
                      disabled={disabled}
                      onClick={() => onRemoveSize(variant.size)}
                      className="text-[11px] leading-none text-muted-foreground hover:text-destructive disabled:opacity-60"
                    >
                      ×
                    </button>
                  </div>
                  <input
                    key={`${variant.size}-${variant.stock}`}
                    id={inputId}
                    type="number"
                    min="0"
                    step="1"
                    defaultValue={variant.stock}
                    disabled={disabled}
                    onBlur={(event) => {
                      const stock = Number(event.target.value)
                      if (stock !== variant.stock) {
                        onSetStock(variant.size, stock)
                      }
                    }}
                    className={
                      variant.stock === 0
                        ? "h-11 border border-input bg-muted text-center text-sm font-semibold text-muted-foreground outline-none focus-visible:border-ring"
                        : "h-11 border border-input bg-background text-center text-sm font-semibold text-foreground outline-none focus-visible:border-ring"
                    }
                  />
                </div>
              )
            })}
          </div>
        )}
        {newSize === null ? (
          <button
            type="button"
            disabled={disabled}
            onClick={() => setNewSize("")}
            className="flex h-10 w-fit items-center gap-2 border border-dashed border-muted-foreground px-3 text-[11px] font-extrabold tracking-[0.06em] text-muted-foreground uppercase hover:text-foreground disabled:opacity-60"
          >
            <PlusIcon size={13} />
            Añadir talla
          </button>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <label htmlFor={`new-size-${colorway.id}`} className="sr-only">
              Nueva talla EU
            </label>
            <input
              id={`new-size-${colorway.id}`}
              type="number"
              min="1"
              max="99.5"
              step="0.5"
              autoFocus
              placeholder="Talla EU"
              value={newSize}
              onChange={(event) => setNewSize(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault()
                  submitNewSize()
                }
              }}
              className={`${fieldClass} w-28`}
            />
            <button
              type="button"
              disabled={disabled}
              onClick={submitNewSize}
              className="h-11 bg-primary px-4 text-[11px] font-extrabold tracking-[0.06em] text-primary-foreground uppercase hover:bg-primary/90 disabled:opacity-60"
            >
              Añadir
            </button>
            <button
              type="button"
              onClick={() => setNewSize(null)}
              className="h-11 border border-input bg-card px-3 text-[11px] font-extrabold tracking-[0.06em] uppercase hover:bg-muted"
            >
              Cancelar
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
