import { cn } from "cn"

import {
  SURFACE_GLYPH_CLASSES,
  SURFACE_TONE_CLASSES,
  SurfaceTone,
} from "@workspace/ui/lib/tones"

type AdminPhotoProps = {
  url: string | null
  alt: string
  tone?: SurfaceTone
  className?: string
  glyphClassName?: string
}

export function AdminPhoto({
  url,
  alt,
  tone = SurfaceTone.TINT,
  className,
  glyphClassName = "w-1/2",
}: AdminPhotoProps) {
  if (url) {
    return (
      <img
        src={url}
        alt={alt}
        loading="lazy"
        className={cn("bg-muted object-cover", className)}
      />
    )
  }
  return (
    <div
      className={cn(
        "relative flex items-center justify-center overflow-hidden",
        SURFACE_TONE_CLASSES[tone],
        className
      )}
    >
      <svg
        viewBox="0 0 240 140"
        className={cn("h-auto", SURFACE_GLYPH_CLASSES[tone], glyphClassName)}
        fill="currentColor"
        aria-hidden="true"
      >
        <path d="M26 100C26 58 40 40 64 40c16 0 24 11 29 24 5 13 15 19 29 19h30c28 0 54 8 70 19z" />
        <rect x="14" y="97" width="212" height="21" rx="10.5" opacity="0.65" />
      </svg>
    </div>
  )
}
