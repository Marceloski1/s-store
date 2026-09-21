import { z } from "zod"

export const namedResourceSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "El nombre es obligatorio")
    .max(100, "Máximo 100 caracteres"),
  slug: z
    .string()
    .trim()
    .max(120, "Máximo 120 caracteres")
    .refine(
      (value) => value === "" || /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value),
      "Solo minúsculas, números y guiones"
    ),
})

export type NamedResourceFormValues = z.output<typeof namedResourceSchema>
