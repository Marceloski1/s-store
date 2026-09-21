import { SneakerStatus } from "@/features/admin/api/types"
import { StatusPill } from "@/features/admin/components/status-pill"

type SneakerEditorHeaderProps = {
  title: string
  status: SneakerStatus | null
  isSaving: boolean
  formId: string
  onArchive: () => void
}

export function SneakerEditorHeader({
  title,
  status,
  isSaving,
  formId,
  onArchive,
}: SneakerEditorHeaderProps) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div className="flex min-w-0 flex-col gap-2">
        <a
          href="/admin"
          className="flex items-center gap-2 text-xs font-bold tracking-[0.06em] text-muted-foreground uppercase hover:text-primary"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="m14.5 6-6 6 6 6" />
          </svg>
          Volver a sneakers
        </a>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="font-display text-3xl leading-none font-extrabold tracking-tight text-foreground uppercase sm:text-4xl">
            {title}
          </h1>
          {status && <StatusPill status={status} />}
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2.5">
        {status === SneakerStatus.ACTIVE && (
          <button
            type="button"
            disabled={isSaving}
            onClick={onArchive}
            className="h-11 border border-input bg-card px-4 text-xs font-extrabold tracking-[0.06em] text-destructive uppercase hover:bg-muted disabled:opacity-60"
          >
            Archivar
          </button>
        )}
        {status === null ? (
          <button
            type="submit"
            form={formId}
            disabled={isSaving}
            className="h-11 bg-primary px-6 text-xs font-extrabold tracking-[0.06em] text-primary-foreground uppercase hover:bg-primary/90 disabled:opacity-60"
          >
            Guardar borrador
          </button>
        ) : (
          <button
            type="submit"
            form={formId}
            disabled={isSaving}
            className="h-11 bg-primary px-6 text-xs font-extrabold tracking-[0.06em] text-primary-foreground uppercase hover:bg-primary/90 disabled:opacity-60"
          >
            {isSaving ? "Guardando…" : "Guardar cambios"}
          </button>
        )}
      </div>
    </div>
  )
}
