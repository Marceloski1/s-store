import { Button } from "@workspace/ui/components/button"

type PaginationControlsProps = {
  page: number
  pages: number
  total: number
  onPageChange: (page: number) => void
}

export function PaginationControls({
  page,
  pages,
  total,
  onPageChange,
}: PaginationControlsProps) {
  return (
    <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
      <span>
        {total} registros · página {pages === 0 ? 0 : page} de {pages}
      </span>
      <div className="flex gap-1">
        <Button
          size="sm"
          variant="outline"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Anterior
        </Button>
        <Button
          size="sm"
          variant="outline"
          disabled={page >= pages}
          onClick={() => onPageChange(page + 1)}
        >
          Siguiente
        </Button>
      </div>
    </div>
  )
}
