import { useState } from "react"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"

import type {
  NamedResourceGateway,
  NamedResourceInput,
} from "@/features/catalog/api/types"
import { NamedResourceForm } from "@/features/catalog/components/named-resource-form"
import { NamedResourceTable } from "@/features/catalog/components/named-resource-table"
import { PaginationControls } from "@/features/catalog/components/pagination-controls"
import { useNamedResource } from "@/features/catalog/hooks/use-named-resource"

type NamedResourceManagerProps = {
  title: string
  gateway: NamedResourceGateway
}

export function NamedResourceManager({
  title,
  gateway,
}: NamedResourceManagerProps) {
  const resource = useNamedResource(gateway)
  const [editingId, setEditingId] = useState<string | null>(null)

  async function handleUpdate(id: string, input: NamedResourceInput) {
    const updated = await resource.update(id, input)
    if (updated) setEditingId(null)
    return updated
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <NamedResourceForm
          submitLabel="Crear"
          isSaving={resource.isSaving}
          onSubmit={resource.create}
        />
        {resource.error && (
          <p role="alert" className="text-xs text-destructive">
            {resource.error}
          </p>
        )}
        {resource.isLoading && (
          <p className="text-sm text-muted-foreground">Cargando…</p>
        )}
        {resource.data && (
          <>
            <NamedResourceTable
              items={resource.data.items}
              editingId={editingId}
              isSaving={resource.isSaving}
              onEdit={setEditingId}
              onCancelEdit={() => setEditingId(null)}
              onUpdate={handleUpdate}
              onDelete={(id) => void resource.remove(id)}
            />
            <PaginationControls
              page={resource.page}
              pages={resource.data.pages}
              total={resource.data.total}
              onPageChange={resource.setPage}
            />
          </>
        )}
      </CardContent>
    </Card>
  )
}
