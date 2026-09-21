import {
  DESCRIPTION_MAX_LENGTH,
  type AdminOption,
  type SneakerForm,
} from "@/features/admin/api/types"
import {
  fieldClass,
  labelClass,
  sectionClass,
  textareaClass,
} from "@/features/admin/components/editor-styles"

type SneakerGeneralSectionProps = {
  form: SneakerForm
  brands: AdminOption[]
  categories: AdminOption[]
  genders: AdminOption[]
  currencies: readonly string[]
  disabled: boolean
  onChange: <K extends keyof SneakerForm>(key: K, value: SneakerForm[K]) => void
  onRegenerateSlug: () => void
}

export function SneakerGeneralSection({
  form,
  brands,
  categories,
  genders,
  currencies,
  disabled,
  onChange,
  onRegenerateSlug,
}: SneakerGeneralSectionProps) {
  return (
    <section className={sectionClass}>
      <div className="border-b border-border px-6 py-4">
        <h2 className="text-[17px] font-extrabold">Datos generales</h2>
      </div>
      <div className="flex flex-col gap-5 px-6 py-5">
        <div className="grid gap-4 sm:grid-cols-[1.4fr_1fr]">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="name" className={labelClass}>
              Nombre del modelo
            </label>
            <input
              id="name"
              type="text"
              required
              value={form.name}
              disabled={disabled}
              onChange={(event) => onChange("name", event.target.value)}
              className={fieldClass}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="slug" className={labelClass}>
              Slug (URL)
            </label>
            <div className="flex gap-2">
              <input
                id="slug"
                type="text"
                value={form.slug}
                placeholder="Se genera a partir del nombre"
                disabled={disabled}
                onChange={(event) => onChange("slug", event.target.value)}
                className={`${fieldClass} min-w-0 grow bg-muted text-muted-foreground`}
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
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="description" className={labelClass}>
            Descripción
          </label>
          <textarea
            id="description"
            rows={3}
            maxLength={DESCRIPTION_MAX_LENGTH}
            value={form.description}
            disabled={disabled}
            onChange={(event) => onChange("description", event.target.value)}
            className={textareaClass}
          />
          <span className="text-[11px] text-muted-foreground">
            {form.description.length} / {DESCRIPTION_MAX_LENGTH} caracteres
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="brand" className={labelClass}>
              Marca
            </label>
            <select
              id="brand"
              value={form.brandId}
              disabled={disabled}
              onChange={(event) => onChange("brandId", event.target.value)}
              className={fieldClass}
            >
              {brands.map((brand) => (
                <option key={brand.value} value={brand.value}>
                  {brand.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="category" className={labelClass}>
              Categoría
            </label>
            <select
              id="category"
              value={form.categoryId}
              disabled={disabled}
              onChange={(event) => onChange("categoryId", event.target.value)}
              className={fieldClass}
            >
              {categories.map((category) => (
                <option key={category.value} value={category.value}>
                  {category.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="gender" className={labelClass}>
              Para quién
            </label>
            <select
              id="gender"
              value={form.gender}
              disabled={disabled}
              onChange={(event) =>
                onChange("gender", event.target.value as SneakerForm["gender"])
              }
              className={fieldClass}
            >
              {genders.map((gender) => (
                <option key={gender.value} value={gender.value}>
                  {gender.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-[1fr_0.7fr_1fr_1fr]">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="price" className={labelClass}>
              Precio base
            </label>
            <input
              id="price"
              type="number"
              min="0"
              step="0.01"
              required
              value={form.price}
              disabled={disabled}
              onChange={(event) => onChange("price", event.target.value)}
              className={fieldClass}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="currency" className={labelClass}>
              Moneda
            </label>
            <select
              id="currency"
              value={form.currency}
              disabled={disabled}
              onChange={(event) => onChange("currency", event.target.value)}
              className={fieldClass}
            >
              {currencies.map((currency) => (
                <option key={currency} value={currency}>
                  {currency}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="release" className={labelClass}>
              Fecha de lanzamiento
            </label>
            <input
              id="release"
              type="date"
              value={form.releaseDate}
              disabled={disabled}
              onChange={(event) => onChange("releaseDate", event.target.value)}
              className={fieldClass}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="reference" className={labelClass}>
              Referencia
            </label>
            <input
              id="reference"
              type="text"
              value={form.reference}
              placeholder="ALS-XXX-000"
              disabled={disabled}
              onChange={(event) => onChange("reference", event.target.value)}
              className={`${fieldClass} uppercase`}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
