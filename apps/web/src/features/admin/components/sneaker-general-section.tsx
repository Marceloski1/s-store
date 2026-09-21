import {
  DESCRIPTION_MAX_LENGTH,
  type AdminOption,
} from "@/features/admin/api/types"
import {
  fieldClass,
  invalidClass,
  labelClass,
  sectionClass,
  textareaClass,
} from "@/features/admin/components/editor-styles"
import { SneakerField } from "@/features/admin/components/form-fields"

type SneakerGeneralSectionProps = {
  brands: AdminOption[]
  categories: AdminOption[]
  genders: AdminOption[]
  currencies: readonly string[]
  disabled: boolean
  onRegenerateSlug: () => void
}

export function SneakerGeneralSection({
  brands,
  categories,
  genders,
  currencies,
  disabled,
  onRegenerateSlug,
}: SneakerGeneralSectionProps) {
  return (
    <section className={sectionClass}>
      <div className="border-b border-border px-6 py-4">
        <h2 className="text-[17px] font-extrabold">Datos generales</h2>
      </div>
      <div className="flex flex-col gap-5 px-6 py-5">
        <div className="grid gap-4 sm:grid-cols-[1.4fr_1fr]">
          <SneakerField
            name="name"
            id="name"
            label="Nombre del modelo"
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
          <SneakerField
            name="slug"
            id="slug"
            label="Slug (URL)"
            labelClassName={labelClass}
            render={({ field, fieldState, control }) => (
              <div className="flex gap-2">
                <input
                  {...control}
                  {...field}
                  type="text"
                  placeholder="Se genera a partir del nombre"
                  className={invalidClass(
                    `${fieldClass} min-w-0 grow bg-muted text-muted-foreground`,
                    fieldState.invalid
                  )}
                />
                <button
                  type="button"
                  disabled={disabled}
                  onClick={onRegenerateSlug}
                  className="h-11 shrink-0 border border-input bg-card px-3 text-[11px] font-extrabold tracking-[0.04em] uppercase hover:bg-muted disabled:opacity-60"
                >
                  Regenerar
                </button>
              </div>
            )}
          />
        </div>

        <SneakerField
          name="description"
          id="description"
          label="Descripción"
          labelClassName={labelClass}
          render={({ field, fieldState, control }) => (
            <>
              <textarea
                {...control}
                {...field}
                rows={3}
                className={invalidClass(textareaClass, fieldState.invalid)}
              />
              <span className="text-[11px] text-muted-foreground">
                {field.value.length} / {DESCRIPTION_MAX_LENGTH} caracteres
              </span>
            </>
          )}
        />

        <div className="grid gap-4 sm:grid-cols-3">
          <SneakerField
            name="brandId"
            id="brand"
            label="Marca"
            labelClassName={labelClass}
            render={({ field, fieldState, control }) => (
              <select
                {...control}
                {...field}
                className={invalidClass(fieldClass, fieldState.invalid)}
              >
                {brands.map((brand) => (
                  <option key={brand.value} value={brand.value}>
                    {brand.label}
                  </option>
                ))}
              </select>
            )}
          />
          <SneakerField
            name="categoryId"
            id="category"
            label="Categoría"
            labelClassName={labelClass}
            render={({ field, fieldState, control }) => (
              <select
                {...control}
                {...field}
                className={invalidClass(fieldClass, fieldState.invalid)}
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            )}
          />
          <SneakerField
            name="gender"
            id="gender"
            label="Para quién"
            labelClassName={labelClass}
            render={({ field, control }) => (
              <select {...control} {...field} className={fieldClass}>
                {genders.map((gender) => (
                  <option key={gender.value} value={gender.value}>
                    {gender.label}
                  </option>
                ))}
              </select>
            )}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-[1fr_0.7fr_1fr_1fr]">
          <SneakerField
            name="price"
            id="price"
            label="Precio base"
            labelClassName={labelClass}
            render={({ field, fieldState, control }) => (
              <input
                {...control}
                {...field}
                type="text"
                inputMode="decimal"
                className={invalidClass(fieldClass, fieldState.invalid)}
              />
            )}
          />
          <SneakerField
            name="currency"
            id="currency"
            label="Moneda"
            labelClassName={labelClass}
            render={({ field, control }) => (
              <select {...control} {...field} className={fieldClass}>
                {currencies.map((currency) => (
                  <option key={currency} value={currency}>
                    {currency}
                  </option>
                ))}
              </select>
            )}
          />
          <SneakerField
            name="releaseDate"
            id="release"
            label="Fecha de lanzamiento"
            labelClassName={labelClass}
            render={({ field, control }) => (
              <input
                {...control}
                {...field}
                type="date"
                className={fieldClass}
              />
            )}
          />
          <SneakerField
            name="reference"
            id="reference"
            label="Referencia"
            labelClassName={labelClass}
            render={({ field, fieldState, control }) => (
              <input
                {...control}
                {...field}
                type="text"
                placeholder="ALS-XXX-000"
                className={invalidClass(
                  `${fieldClass} uppercase`,
                  fieldState.invalid
                )}
              />
            )}
          />
        </div>
      </div>
    </section>
  )
}
