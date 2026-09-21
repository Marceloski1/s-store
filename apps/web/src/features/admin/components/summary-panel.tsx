import { formatAdminDate } from "@/features/admin/api/types"

type SummaryPanelProps = {
  stock: number
  colorways: number
  images: number
  updatedAt: string
}

export function SummaryPanel({
  stock,
  colorways,
  images,
  updatedAt,
}: SummaryPanelProps) {
  const rows = [
    { label: "Pares en stock", value: stock },
    { label: "Colores", value: colorways },
    { label: "Fotos", value: images },
    { label: "Actualizado", value: formatAdminDate(updatedAt) },
  ]
  return (
    <section className="flex flex-col gap-3 border border-border bg-card p-5">
      <h2 className="text-[15px] font-extrabold">Resumen</h2>
      {rows.map((row) => (
        <div
          key={row.label}
          className="flex items-center justify-between text-[13px]"
        >
          <span className="text-muted-foreground">{row.label}</span>
          <span className="font-bold">{row.value}</span>
        </div>
      ))}
    </section>
  )
}
