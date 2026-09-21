import type { SneakerForm } from "@/features/admin/api/types"
import {
  fieldClass,
  invalidClass,
  labelClass,
  sectionClass,
  textareaClass,
} from "@/features/admin/components/editor-styles"
import { SneakerField } from "@/features/admin/components/form-fields"

const SPEC_FIELDS = [
  { key: "material", label: "Material" },
  { key: "technology", label: "Tecnología" },
  { key: "weight", label: "Peso" },
  { key: "cushioning", label: "Amortiguación" },
] as const satisfies readonly { key: keyof SneakerForm; label: string }[]

export function SneakerContentSection() {
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
          {SPEC_FIELDS.map((spec) => (
            <SneakerField
              key={spec.key}
              name={spec.key}
              id={spec.key}
              label={spec.label}
              labelClassName={labelClass}
              render={({ field, fieldState, control }) => (
                <input
                  {...control}
                  {...field}
                  type="text"
                  className={invalidClass(fieldClass, fieldState.invalid)}
                />
              )}
            />
          ))}
        </div>

        <SneakerField
          name="usage"
          id="usage"
          label="Recomendación de uso o estilo"
          labelClassName={labelClass}
          render={({ field, fieldState, control }) => (
            <textarea
              {...control}
              {...field}
              rows={2}
              className={invalidClass(textareaClass, fieldState.invalid)}
            />
          )}
        />

        <div className="grid gap-4 sm:grid-cols-[1.7fr_1fr]">
          <SneakerField
            name="testimonialQuote"
            id="testimonial"
            label="Testimonio de cliente"
            labelClassName={labelClass}
            render={({ field, fieldState, control }) => (
              <textarea
                {...control}
                {...field}
                rows={2}
                placeholder="Todavía sin testimonio"
                className={invalidClass(textareaClass, fieldState.invalid)}
              />
            )}
          />
          <SneakerField
            name="testimonialAuthor"
            id="testimonial-author"
            label="Quién lo dice"
            labelClassName={labelClass}
            render={({ field, fieldState, control }) => (
              <input
                {...control}
                {...field}
                type="text"
                placeholder="Nombre y talla"
                className={invalidClass(fieldClass, fieldState.invalid)}
              />
            )}
          />
        </div>
      </div>
    </section>
  )
}
