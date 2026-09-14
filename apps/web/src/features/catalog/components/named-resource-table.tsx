import { Button } from "@workspace/ui/components/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"

import type {
  NamedResource,
  NamedResourceInput,
} from "@/features/catalog/api/types"
import { NamedResourceForm } from "@/features/catalog/components/named-resource-form"

type NamedResourceTableProps = {
  items: NamedResource[]
  editingId: string | null
  isSaving: boolean
  onEdit: (id: string) => void
  onCancelEdit: () => void
  onUpdate: (id: string, input: NamedResourceInput) => Promise<boolean>
  onDelete: (id: string) => void
}

export function NamedResourceTable({
  items,
  editingId,
  isSaving,
  onEdit,
  onCancelEdit,
  onUpdate,
  onDelete,
}: NamedResourceTableProps) {
  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">Sin registros</p>
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Nombre</TableHead>
          <TableHead>Slug</TableHead>
          <TableHead className="text-end">Acciones</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((item) =>
          item.id === editingId ? (
            <TableRow key={item.id}>
              <TableCell colSpan={3}>
                <NamedResourceForm
                  initialValue={item}
                  submitLabel="Guardar"
                  isSaving={isSaving}
                  onSubmit={(input) => onUpdate(item.id, input)}
                  onCancel={onCancelEdit}
                />
              </TableCell>
            </TableRow>
          ) : (
            <TableRow key={item.id}>
              <TableCell>{item.name}</TableCell>
              <TableCell className="font-mono text-muted-foreground">
                {item.slug}
              </TableCell>
              <TableCell className="flex justify-end gap-1">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onEdit(item.id)}
                >
                  Editar
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  disabled={isSaving}
                  onClick={() => onDelete(item.id)}
                >
                  Eliminar
                </Button>
              </TableCell>
            </TableRow>
          )
        )}
      </TableBody>
    </Table>
  )
}
