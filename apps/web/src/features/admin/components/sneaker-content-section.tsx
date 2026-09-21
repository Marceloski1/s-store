import type { SneakerForm } from "@/features/admin/api/types"
import {
  fieldClass,
  labelClass,
  sectionClass,
  textareaClass,
} from "@/features/admin/components/editor-styles"

type SneakerContentSectionProps = {
  form: SneakerForm
  disabled: boolean
  onChange: <K extends keyof SneakerForm>(key: K, value: SneakerForm[K]) => void
}

const SPEC_FIELDS = [
  { key: "material", label: "Material" },
  { key: "technology", label: "Tecnología" },
  { key: "weight", label: "Peso" },
  { key: "cushioning", label: "Amortiguación" },
] as const satisfies readonly { key: keyof SneakerForm; label: string }[]

export function SneakerContentSection({
  form,
  disabled,
  onChange,
}: SneakerContentSectionProps) {
  return (
    <section className={sectionClass}>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-6 py-4">
        <h2 className="text-[17px] font-extrabold">
          Ficha técnica y textos de venta
        </h2>
        <span className="text-xs text-muted-foreground">
          Se muestran en la página pública del modelo
        </span>
      </div>
      <div className="flex flex-col gap-5 px-6 py-5">
        <div className="grid gap-4 sm:grid-cols-2">
          {SPEC_FIELDS.map((field) => (
            <div key={field.key} className="flex flex-col gap-1.5">
              <label htmlFor={field.key} className={labelClass}>
                {field.label}
              </label>
              <input
                id={field.key}
                type="text"
                maxLength={100}
                value={form[field.key]}
                disabled={disabled}
                onChange={(event) => onChange(field.key, event.target.value)}
                className={fieldClass}
              />
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="usage" className={labelClass}>
            Recomendación de uso o estilo
          </label>
          <textarea
            id="usage"
            rows={2}
            maxLength={500}
            value={form.usage}
            disabled={disabled}
            onChange={(event) => onChange("usage", event.target.value)}
            className={textareaClass}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-[1.7fr_1fr]">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="testimonial" className={labelClass}>
              Testimonio de cliente
            </label>
            <textarea
              id="testimonial"
              rows={2}
              maxLength={500}
              placeholder="Todavía sin testimonio"
              value={form.testimonialQuote}
              disabled={disabled}
              onChange={(event) =>
                onChange("testimonialQuote", event.target.value)
              }
              className={textareaClass}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="testimonial-author" className={labelClass}>
              Quién lo dice
            </label>
            <input
              id="testimonial-author"
              type="text"
              maxLength={100}
              placeholder="Nombre y talla"
              value={form.testimonialAuthor}
              disabled={disabled}
              onChange={(event) =>
                onChange("testimonialAuthor", event.target.value)
              }
              className={fieldClass}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
