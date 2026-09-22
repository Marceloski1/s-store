import { cn } from "cn"

import { SneakerSilhouetteIcon } from "@workspace/ui/components/icons/sneaker-silhouette"
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
      <SneakerSilhouetteIcon
        className={cn("h-auto", SURFACE_GLYPH_CLASSES[tone], glyphClassName)}
      />
    </div>
  )
}
