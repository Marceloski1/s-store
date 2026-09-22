export enum SurfaceTone {
  TINT = "TINT",
  SOFT = "SOFT",
  NONE = "NONE",
}

export enum AccentTone {
  PRIMARY = "PRIMARY",
  SUCCESS = "SUCCESS",
  WARNING = "WARNING",
  MUTED = "MUTED",
}

export const SURFACE_TONE_CLASSES: Record<SurfaceTone, string> = {
  [SurfaceTone.TINT]: "bg-accent",
  [SurfaceTone.SOFT]: "bg-muted",
  [SurfaceTone.NONE]: "",
}

export const SURFACE_GLYPH_CLASSES: Record<SurfaceTone, string> = {
  [SurfaceTone.TINT]: "text-primary/25",
  [SurfaceTone.SOFT]: "text-foreground/15",
  [SurfaceTone.NONE]: "text-primary/25",
}

export const ACCENT_TONE_BORDER_CLASSES: Record<AccentTone, string> = {
  [AccentTone.PRIMARY]: "border-t-primary",
  [AccentTone.SUCCESS]: "border-t-success",
  [AccentTone.WARNING]: "border-t-warning",
  [AccentTone.MUTED]: "border-t-muted-foreground",
}

export function alternatingTone(index: number): SurfaceTone {
  return index % 2 === 0 ? SurfaceTone.TINT : SurfaceTone.SOFT
}
