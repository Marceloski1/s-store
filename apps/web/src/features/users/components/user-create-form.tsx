import { Form, FormField } from "@workspace/ui/components/form"

import {
  fieldClass,
  labelClass,
  sectionClass,
} from "@/features/admin/components/editor-styles"
import {
  createUserSchema,
  PASSWORD_MIN_LENGTH,
  type CreateUserValues,
} from "@/features/auth/api/schemas"

type UserCreateFormProps = {
  disabled: boolean
  onSubmit: (values: CreateUserValues) => Promise<boolean>
}

const EMPTY_USER: CreateUserValues = { name: "", email: "", password: "" }

export function UserCreateForm({ disabled, onSubmit }: UserCreateFormProps) {
  return (
    <section className={sectionClass}>
      <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-border px-6 py-4">
        <h2 className="text-[17px] font-extrabold">Nuevo administrador</h2>
        <span className="text-xs text-muted-foreground">
          Podrá gestionar el catálogo, pero no usuarios
        </span>
      </div>
      <Form
        schema={createUserSchema}
        defaultValues={EMPTY_USER}
        disabled={disabled}
        onSubmit={async (values, form) => {
          if (await onSubmit(values)) form.reset(EMPTY_USER)
        }}
        className="grid items-start gap-4 px-6 py-5 md:grid-cols-[1fr_1.2fr_1fr_auto]"
      >
        <FormField<CreateUserValues, "name">
          name="name"
          label="Nombre"
          labelClassName={labelClass}
          render={({ field, control }) => (
            <input
              {...control}
              {...field}
              type="text"
              autoComplete="off"
              className={`${fieldClass} aria-invalid:border-destructive`}
            />
          )}
        />
        <FormField<CreateUserValues, "email">
          name="email"
          label="Correo"
          labelClassName={labelClass}
          render={({ field, control }) => (
            <input
              {...control}
              {...field}
              type="email"
              autoComplete="off"
              className={`${fieldClass} aria-invalid:border-destructive`}
            />
          )}
        />
        <FormField<CreateUserValues, "password">
          name="password"
          label="Contraseña inicial"
          labelClassName={labelClass}
          description={`Mínimo ${PASSWORD_MIN_LENGTH} caracteres`}
          render={({ field, control }) => (
            <input
              {...control}
              {...field}
              type="password"
              autoComplete="new-password"
              className={`${fieldClass} aria-invalid:border-destructive`}
            />
          )}
        />
        <button
          type="submit"
          disabled={disabled}
          className="h-11 bg-primary px-5 text-xs font-extrabold tracking-[0.06em] text-primary-foreground uppercase hover:bg-primary/90 disabled:opacity-60 md:mt-[22px]"
        >
          Crear
        </button>
      </Form>
    </section>
  )
}
