import { cn } from "cn"

import { STATUS_LABELS, SneakerStatus } from "@/features/admin/api/types"

const TONES: Record<SneakerStatus, string> = {
  [SneakerStatus.ACTIVE]: "bg-success/10 text-success",
  [SneakerStatus.DRAFT]: "bg-warning/10 text-warning",
  [SneakerStatus.ARCHIVED]: "bg-muted text-muted-foreground",
}

export function StatusPill({ status }: { status: SneakerStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-1.5 text-[11px] font-extrabold tracking-[0.04em]",
        TONES[status]
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  )
}
