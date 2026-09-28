"use client"

import {
  createColumnHelper,
  tableFeatures,
  useTable,
} from "@tanstack/react-table"
import { cn } from "cn"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@workspace/ui/components/table"

export const dataTableFeatures = tableFeatures({})

export function createDataTableHelper<TData>() {
  return createColumnHelper<typeof dataTableFeatures, TData>()
}

type DataTableProps<TData> = {
  columns: ReturnType<
    ReturnType<typeof createColumnHelper<typeof dataTableFeatures, TData>>["columns"]
  >
  data: TData[]
  className?: string
  page?: number
  pageCount?: number
  onPageChange?: (page: number) => void
}

function DataTable<TData>({ columns, data, className, page, pageCount, onPageChange }: DataTableProps<TData>) {
  const table = useTable({
    features: dataTableFeatures,
    columns,
    data,
  })

  return (
    <>
      <Table className={className}>
      <TableHeader>
        {table.getHeaderGroups().map((group) => (
          <TableRow key={group.id}>
            {group.headers.map((header) => (
              <TableHead key={header.id}>
                {header.isPlaceholder ? null : (
                  <table.FlexRender header={header} />
                )}
              </TableHead>
            ))}
          </TableRow>
        ))}
      </TableHeader>
      <TableBody>
        {table.getRowModel().rows.length === 0 ? (
          <TableRow>
            <TableCell
              colSpan={table.getAllColumns().length}
              className={cn("h-24 text-center text-muted-foreground")}
            >
              Sin registros
            </TableCell>
          </TableRow>
        ) : (
          table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getAllCells().map((cell) => (
                <TableCell key={cell.id}>
                  <table.FlexRender cell={cell} />
                </TableCell>
              ))}
            </TableRow>
          ))
        )}
      </TableBody>
      </Table>
      {page !== undefined && pageCount !== undefined && pageCount > 1 && (
      <div className="flex items-center justify-between border-t border-border px-4 py-3 text-xs text-muted-foreground">
        <span>Página {page} de {pageCount}</span>
        <div className="flex gap-2">
          <button type="button" disabled={page <= 1} onClick={() => onPageChange?.(page - 1)} className="border border-border px-3 py-1.5 disabled:opacity-40">Anterior</button>
          <button type="button" disabled={page >= pageCount} onClick={() => onPageChange?.(page + 1)} className="border border-border px-3 py-1.5 disabled:opacity-40">Siguiente</button>
        </div>
      </div>
      )}
    </>
  )
}

export { DataTable }
