import { Button } from "@workspace/ui/components/button"
import { Form, FormField } from "@workspace/ui/components/form"
import { Input } from "@workspace/ui/components/input"

import {
  namedResourceSchema,
  type NamedResourceFormValues,
} from "@/features/catalog/api/schemas"
import type { NamedResourceInput } from "@/features/catalog/api/types"

type NamedResourceFormProps = {
  initialValue?: NamedResourceInput
  submitLabel: string
  isSaving: boolean
  onSubmit: (input: NamedResourceInput) => Promise<boolean>
  onCancel?: () => void
}

export function NamedResourceForm({
  initialValue,
  submitLabel,
  isSaving,
  onSubmit,
  onCancel,
}: NamedResourceFormProps) {
  return (
    <Form
      schema={namedResourceSchema}
      defaultValues={{
        name: initialValue?.name ?? "",
        slug: initialValue?.slug ?? "",
      }}
      onSubmit={async (values, form) => {
        const saved = await onSubmit({
          name: values.name,
          slug: values.slug || null,
        })
        if (saved && !initialValue) form.reset({ name: "", slug: "" })
      }}
      className="flex flex-wrap items-start gap-2"
    >
      <FormField<NamedResourceFormValues, "name">
        name="name"
        label="Nombre"
        className="grid min-w-40 flex-1 gap-1"
        render={({ field, control }) => <Input {...control} {...field} />}
      />
      <FormField<NamedResourceFormValues, "slug">
        name="slug"
        label="Slug"
        className="grid min-w-40 flex-1 gap-1"
        render={({ field, control }) => (
          <Input {...control} {...field} placeholder="Automático" />
        )}
      />
      <div className="flex gap-2 pt-5">
        <Button type="submit" disabled={isSaving}>
          {submitLabel}
        </Button>
        {onCancel && (
          <Button type="button" variant="ghost" onClick={onCancel}>
            Cancelar
          </Button>
        )}
      </div>
    </Form>
  )
}
