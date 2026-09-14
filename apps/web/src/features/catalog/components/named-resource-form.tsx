import { useId, useState, type FormEvent } from "react"

import { Button } from "@workspace/ui/components/button"
import { Input } from "@workspace/ui/components/input"
import { Label } from "@workspace/ui/components/label"

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
  const nameId = useId()
  const slugId = useId()
  const [name, setName] = useState(initialValue?.name ?? "")
  const [slug, setSlug] = useState(initialValue?.slug ?? "")

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const saved = await onSubmit({ name, slug: slug.trim() || null })
    if (saved && !initialValue) {
      setName("")
      setSlug("")
    }
  }

  return (
    <form
      onSubmit={(event) => void handleSubmit(event)}
      className="flex flex-wrap items-end gap-2"
    >
      <div className="grid min-w-40 flex-1 gap-1">
        <Label htmlFor={nameId}>Nombre</Label>
        <Input
          id={nameId}
          value={name}
          onChange={(event) => setName(event.target.value)}
          maxLength={100}
          required
        />
      </div>
      <div className="grid min-w-40 flex-1 gap-1">
        <Label htmlFor={slugId}>Slug</Label>
        <Input
          id={slugId}
          value={slug}
          onChange={(event) => setSlug(event.target.value)}
          placeholder="Automático"
          pattern="[a-z0-9]+(-[a-z0-9]+)*"
          maxLength={120}
        />
      </div>
      <Button type="submit" disabled={isSaving}>
        {submitLabel}
      </Button>
      {onCancel && (
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancelar
        </Button>
      )}
    </form>
  )
}
