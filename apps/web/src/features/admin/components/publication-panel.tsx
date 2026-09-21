import {
  PublishCheckState,
  STATUS_LABELS,
  type PublishCheck,
  type SneakerStatus,
} from "@/features/admin/api/types"
import {
  fieldClass,
  labelClass,
  sectionClass,
} from "@/features/admin/components/editor-styles"

type PublicationPanelProps = {
  checks: PublishCheck[]
  status: SneakerStatus
  disabled: boolean
  canChangeStatus: (target: SneakerStatus) => boolean
  onChangeStatus: (target: SneakerStatus) => void
}

const STATUS_ORDER: SneakerStatus[] = ["draft", "active", "archived"]

export function PublicationPanel({
  checks,
  status,
  disabled,
  canChangeStatus,
  onChangeStatus,
}: PublicationPanelProps) {
  return (
    <section className={sectionClass}>
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-[15px] font-extrabold">Publicación</h2>
      </div>
      <div className="flex flex-col gap-4 px-5 py-4">
        <div className="flex flex-col gap-2.5">
          {checks.map((check) => (
            <span
              key={check.label}
              className={
                check.state === PublishCheckState.OK
                  ? "flex items-center gap-2.5 text-[13px] font-semibold text-foreground"
                  : "flex items-center gap-2.5 text-[13px] font-semibold text-warning"
              }
            >
              {check.state === PublishCheckState.OK ? (
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="text-success"
                  aria-hidden="true"
                >
                  <path d="m5 12.5 4.5 4.5L19 7.5" />
                </svg>
              ) : (
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="8.5" />
                  <path d="M12 8v4.5M12 16h0" />
                </svg>
              )}
              {check.label}
            </span>
          ))}
        </div>
        <div className="flex flex-col gap-1.5 border-t border-border pt-4">
          <label htmlFor="status" className={labelClass}>
            Estado
          </label>
          <select
            id="status"
            value={status}
            disabled={disabled}
            onChange={(event) =>
              onChangeStatus(event.target.value as SneakerStatus)
            }
            className={fieldClass}
          >
            {STATUS_ORDER.map((option) => (
              <option
                key={option}
                value={option}
                disabled={!canChangeStatus(option)}
              >
                {STATUS_LABELS[option]}
              </option>
            ))}
          </select>
          <span className="text-[11px] leading-relaxed text-muted-foreground">
            Un modelo publicado solo puede archivarse; para volver a editarlo a
            fondo, pásalo a borrador desde archivados.
          </span>
        </div>
      </div>
    </section>
  )
}
