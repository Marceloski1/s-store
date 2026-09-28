import { useState } from "react"

import { EyeIcon } from "@workspace/ui/components/icons/eye"
import { StrokeIcon } from "@workspace/ui/components/icons/stroke-icon"
import { Form, FormField } from "@workspace/ui/components/form"

import { loginSchema, type LoginValues } from "@/features/auth/api/schemas"
import { useLogin } from "@/features/auth/hooks/use-login"

type LoginFormProps = {
  nextPath: string | null
}

const labelClass =
  "text-xs font-extrabold tracking-[0.1em] text-foreground uppercase"
const inputClass =
  "h-14 w-full border border-input bg-background px-4 text-[15px] font-medium outline-none focus-visible:border-ring aria-invalid:border-destructive"

export function LoginForm({ nextPath }: LoginFormProps) {
  const { error, isSubmitting, login } = useLogin(nextPath)
  const [showPassword, setShowPassword] = useState(false)

  return (
    <Form
      schema={loginSchema}
      defaultValues={{ email: "", password: "" }}
      onSubmit={login}
      className="flex flex-col gap-6"
    >
      <FormField<LoginValues, "email">
        name="email"
        id="login-email"
        label="Correo"
        labelClassName={labelClass}
        className="flex flex-col gap-2"
        render={({ field, control }) => (
          <input
            {...control}
            {...field}
            type="email"
            autoComplete="username"
            placeholder="tucorreo@alesa.cu"
            className={inputClass}
          />
        )}
      />

      <FormField<LoginValues, "password">
        name="password"
        id="login-password"
        label="Contraseña"
        labelClassName={labelClass}
        className="flex flex-col gap-2"
        render={({ field, control }) => (
          <div className="relative flex items-center">
            <input
              {...control}
              {...field}
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              className={`${inputClass} pr-14`}
            />
            <button
              type="button"
              aria-label={
                showPassword ? "Ocultar la contraseña" : "Mostrar la contraseña"
              }
              aria-pressed={showPassword}
              onClick={() => setShowPassword((current) => !current)}
              className="absolute right-1.5 flex size-11 items-center justify-center text-muted-foreground hover:text-foreground"
            >
              {showPassword ? (
                <StrokeIcon size={19} strokeWidth={1.8}>
                  <path d="m3 3 18 18" />
                  <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
                  <path d="M9.9 5.2A11.6 11.6 0 0 1 12 5c6 0 9.5 7 9.5 7a17 17 0 0 1-3.1 3.8M6.2 6.3C3.8 8 2.5 12 2.5 12s3.5 7 9.5 7c1.1 0 2.1-.2 3-.6" />
                </StrokeIcon>
              ) : (
                <EyeIcon />
              )}
            </button>
          </div>
        )}
      />

      {error && (
        <p
          role="alert"
          className="border border-destructive/40 bg-destructive/10 px-4 py-3 text-[13px] font-semibold text-destructive"
        >
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex h-14 items-center justify-center bg-primary text-sm font-extrabold tracking-[0.1em] text-primary-foreground uppercase hover:bg-primary/90 disabled:opacity-60"
      >
        {isSubmitting ? "Entrando…" : "Entrar"}
      </button>
    </Form>
  )
}
