import { z } from "zod"

const SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/
const CODE_PATTERN = /^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/
const PRICE_PATTERN = /^\d+(?:\.\d{1,2})?$/
const COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/

function maxText(max: number) {
  return z.string().max(max, `Máximo ${max} caracteres`)
}

function optionalMatch(pattern: RegExp, message: string, max: number) {
  return z
    .string()
    .trim()
    .max(max, `Máximo ${max} caracteres`)
    .refine((value) => value === "" || pattern.test(value), message)
}

const price = z
  .string()
  .trim()
  .regex(PRICE_PATTERN, "Precio no válido: usa números con hasta 2 decimales")

export const sneakerFormSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(1, "El nombre del modelo es obligatorio")
      .max(150, "Máximo 150 caracteres"),
    slug: optionalMatch(
      SLUG_PATTERN,
      "Solo minúsculas, números y guiones",
      120
    ),
    reference: optionalMatch(
      CODE_PATTERN,
      "Solo letras, números y guiones",
      64
    ),
    description: maxText(2000),
    brandId: z.string().min(1, "Elige una marca"),
    categoryId: z.string().min(1, "Elige una categoría"),
    gender: z.enum(["men", "women", "unisex", "kids"]),
    price,
    currency: z.string().regex(/^[A-Z]{3}$/, "Moneda no válida"),
    releaseDate: z.string(),
    material: maxText(100),
    technology: maxText(100),
    weight: maxText(100),
    cushioning: maxText(100),
    usage: maxText(500),
    testimonialQuote: maxText(500),
    testimonialAuthor: maxText(100),
  })
  .superRefine((values, context) => {
    const hasQuote = values.testimonialQuote.trim() !== ""
    const hasAuthor = values.testimonialAuthor.trim() !== ""
    if (hasQuote && !hasAuthor) {
      context.addIssue({
        code: "custom",
        path: ["testimonialAuthor"],
        message: "Indica quién lo dice o borra el testimonio",
      })
    }
    if (hasAuthor && !hasQuote) {
      context.addIssue({
        code: "custom",
        path: ["testimonialQuote"],
        message: "Escribe el testimonio o borra el autor",
      })
    }
  })

export const colorwayFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "El nombre del color es obligatorio")
    .max(100, "Máximo 100 caracteres"),
  colorCode: z.string().regex(COLOR_PATTERN, "Color no válido"),
  sku: z
    .string()
    .trim()
    .min(1, "El SKU es obligatorio")
    .max(64, "Máximo 64 caracteres")
    .regex(CODE_PATTERN, "Solo letras, números y guiones"),
  priceOverride: z
    .string()
    .trim()
    .refine(
      (value) => value === "" || PRICE_PATTERN.test(value),
      "Precio no válido: usa números con hasta 2 decimales"
    ),
})

export type SneakerForm = z.output<typeof sneakerFormSchema>
export type ColorwayInput = z.output<typeof colorwayFormSchema>
