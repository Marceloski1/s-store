import { useRef, useState } from "react"

import { MAX_IMAGES } from "@/features/admin/api/types"
import { AdminPhoto } from "@/features/admin/components/admin-photo"
import { sectionClass } from "@/features/admin/components/editor-styles"
import type { ApiImage } from "@/lib/api/types"

type PhotosPanelProps = {
  images: ApiImage[]
  disabled: boolean
  onUpload: (files: File[]) => void
  onMakePrimary: (imageId: string) => void
  onRemove: (imageId: string) => void
  onMove: (imageId: string, targetIndex: number) => void
}

const smallButtonClass =
  "flex size-7 items-center justify-center border border-input bg-background hover:bg-muted disabled:opacity-40"

export function PhotosPanel({
  images,
  disabled,
  onUpload,
  onMakePrimary,
  onRemove,
  onMove,
}: PhotosPanelProps) {
  const fileInput = useRef<HTMLInputElement>(null)
  const [draggedId, setDraggedId] = useState<string | null>(null)
  const isFull = images.length >= MAX_IMAGES

  return (
    <section className={sectionClass}>
      <div className="flex items-center justify-between border-b border-border px-5 py-4">
        <h2 className="text-[15px] font-extrabold">Fotos</h2>
        <span className="text-xs text-muted-foreground">
          {images.length} de {MAX_IMAGES}
        </span>
      </div>
      <div className="flex flex-col gap-3.5 px-5 py-4">
        {images.length > 0 ? (
          <div className="grid grid-cols-2 gap-3">
            {images.map((image, index) => (
              <div
                key={image.id}
                draggable={!disabled}
                onDragStart={() => setDraggedId(image.id)}
                onDragEnd={() => setDraggedId(null)}
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                  event.preventDefault()
                  if (draggedId && draggedId !== image.id) {
                    onMove(draggedId, index)
                  }
                  setDraggedId(null)
                }}
                className={
                  draggedId === image.id ? "relative opacity-50" : "relative"
                }
              >
                <AdminPhoto
                  url={image.url}
                  alt={image.alt || `Foto ${index + 1}`}
                  tone={image.is_primary ? "tint" : "soft"}
                  className={
                    image.is_primary
                      ? "h-[122px] w-full border-2 border-primary"
                      : "h-[122px] w-full border border-border"
                  }
                  glyphClassName="w-[62%]"
                />
                {image.is_primary ? (
                  <span className="absolute top-2 left-2 bg-primary px-2 py-1 text-[9px] font-extrabold tracking-[0.08em] text-primary-foreground uppercase">
                    Principal
                  </span>
                ) : (
                  <button
                    type="button"
                    disabled={disabled}
                    onClick={() => onMakePrimary(image.id)}
                    className="absolute bottom-2 left-2 border border-input bg-background px-2 py-1 text-[9px] font-extrabold tracking-[0.06em] uppercase hover:bg-muted disabled:opacity-60"
                  >
                    Hacer principal
                  </button>
                )}
                <button
                  type="button"
                  aria-label={`Quitar la foto ${index + 1}`}
                  disabled={disabled}
                  onClick={() => {
                    if (window.confirm("¿Quitar esta foto?")) {
                      onRemove(image.id)
                    }
                  }}
                  className="absolute top-1.5 right-1.5 flex size-7 items-center justify-center border border-input bg-background text-destructive hover:bg-muted disabled:opacity-60"
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.4"
                    strokeLinecap="round"
                    aria-hidden="true"
                  >
                    <path d="M6 6l12 12M18 6 6 18" />
                  </svg>
                </button>
                <div className="absolute right-1.5 bottom-1.5 flex gap-1">
                  <button
                    type="button"
                    aria-label={`Mover la foto ${index + 1} antes`}
                    disabled={disabled || index === 0}
                    onClick={() => onMove(image.id, index - 1)}
                    className={smallButtonClass}
                  >
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.4"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <path d="m14.5 6-6 6 6 6" />
                    </svg>
                  </button>
                  <button
                    type="button"
                    aria-label={`Mover la foto ${index + 1} después`}
                    disabled={disabled || index === images.length - 1}
                    onClick={() => onMove(image.id, index + 1)}
                    className={smallButtonClass}
                  >
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.4"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <path d="m9.5 6 6 6-6 6" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="border border-dashed border-warning bg-warning/10 p-3 text-[13px] font-semibold text-warning">
            Este modelo no tiene fotos. Sube al menos una para poder publicarlo.
          </p>
        )}

        <input
          ref={fileInput}
          type="file"
          accept="image/jpeg,image/png"
          multiple
          className="sr-only"
          tabIndex={-1}
          aria-hidden="true"
          onChange={(event) => {
            onUpload(Array.from(event.target.files ?? []))
            event.target.value = ""
          }}
        />
        <button
          type="button"
          disabled={disabled || isFull}
          onClick={() => fileInput.current?.click()}
          className="flex h-24 flex-col items-center justify-center gap-1.5 border-[1.5px] border-dashed border-muted-foreground bg-muted/40 hover:bg-muted disabled:opacity-60"
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.9"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-primary"
            aria-hidden="true"
          >
            <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" />
            <path d="M4 16v2.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5V16" />
          </svg>
          <span className="text-xs font-extrabold tracking-[0.06em] text-primary uppercase">
            Subir fotos
          </span>
          <span className="text-[11px] text-muted-foreground">
            JPG o PNG · hasta {MAX_IMAGES} por modelo
          </span>
        </button>

        <span className="text-[11px] leading-relaxed text-muted-foreground">
          Arrastra las miniaturas o usa las flechas para cambiar el orden. Al
          borrar una foto se elimina también del almacenamiento.
        </span>
      </div>
    </section>
  )
}
