import { z } from "zod"

export const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, "Escribe tu correo")
    .pipe(z.email("Correo no válido")),
  password: z.string().min(1, "Escribe tu contraseña"),
})

export const PASSWORD_MIN_LENGTH = 8

export const password = z
  .string()
  .min(PASSWORD_MIN_LENGTH, `Mínimo ${PASSWORD_MIN_LENGTH} caracteres`)
  .max(128, "Máximo 128 caracteres")

export const createUserSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "El nombre es obligatorio")
    .max(100, "Máximo 100 caracteres"),
  email: z
    .string()
    .trim()
    .min(1, "El correo es obligatorio")
    .pipe(z.email("Correo no válido")),
  password,
})

export const resetPasswordSchema = z.object({ password })

export type LoginValues = z.output<typeof loginSchema>
export type CreateUserValues = z.output<typeof createUserSchema>
export type ResetPasswordValues = z.output<typeof resetPasswordSchema>
