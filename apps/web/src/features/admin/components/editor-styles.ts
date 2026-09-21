export const fieldClass =
  "h-11 border border-input bg-background px-3 text-sm font-semibold text-foreground outline-none focus-visible:border-ring disabled:opacity-60"

export const labelClass =
  "text-[11px] font-extrabold tracking-[0.1em] text-muted-foreground uppercase"

export const smallLabelClass =
  "text-[10px] font-extrabold tracking-[0.08em] text-muted-foreground uppercase"

export const textareaClass =
  "border border-input bg-background p-3 text-sm leading-relaxed outline-none focus-visible:border-ring disabled:opacity-60"

export const sectionClass = "border border-border bg-card"

export function invalidClass(base: string, invalid: boolean): string {
  return invalid ? `${base} border-destructive` : base
}
