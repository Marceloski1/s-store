import {
  publishChecks,
  sneakerStock,
  type AdminOption,
  type SneakerForm,
} from "@/features/admin/api/types"
import { ColorwaysSection } from "@/features/admin/components/colorways-section"
import { PhotosPanel } from "@/features/admin/components/photos-panel"
import { PublicationPanel } from "@/features/admin/components/publication-panel"
import { SneakerContentSection } from "@/features/admin/components/sneaker-content-section"
import { SneakerEditorHeader } from "@/features/admin/components/sneaker-editor-header"
import { SneakerGeneralSection } from "@/features/admin/components/sneaker-general-section"
import { SummaryPanel } from "@/features/admin/components/summary-panel"
import { useSneakerEditor } from "@/features/admin/hooks/use-sneaker-editor"
import type { ApiSneaker } from "@/lib/api/types"

type SneakerEditorProps = {
  initialSneaker: ApiSneaker | null
  initialForm: SneakerForm
  brands: AdminOption[]
  categories: AdminOption[]
  genders: AdminOption[]
  currencies: readonly string[]
}

export function SneakerEditor({
  initialSneaker,
  initialForm,
  brands,
  categories,
  genders,
  currencies,
}: SneakerEditorProps) {
  const editor = useSneakerEditor(initialSneaker, initialForm)
  const { sneaker, form, isSaving } = editor

  return (
    <div className="flex flex-col gap-5">
      <SneakerEditorHeader
        title={sneaker?.name ?? (form.name.trim() || "Nuevo sneaker")}
        status={sneaker?.status ?? null}
        isSaving={isSaving}
        onArchive={() => void editor.changeStatus("archived")}
        onSave={() => void editor.save()}
      />

      {(editor.error || editor.notice) && (
        <p
          role={editor.error ? "alert" : "status"}
          className={
            editor.error
              ? "border border-destructive/40 bg-destructive/10 px-4 py-3 text-[13px] font-semibold text-destructive"
              : "border border-success/40 bg-success/10 px-4 py-3 text-[13px] font-semibold text-success"
          }
        >
          {editor.error ?? editor.notice}
        </p>
      )}

      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="flex min-w-0 flex-col gap-5">
          <form
            className="flex flex-col gap-5"
            onSubmit={(event) => {
              event.preventDefault()
              void editor.save()
            }}
          >
            <SneakerGeneralSection
              form={form}
              brands={brands}
              categories={categories}
              genders={genders}
              currencies={currencies}
              disabled={isSaving}
              onChange={editor.setField}
              onRegenerateSlug={editor.regenerateSlug}
            />
            <SneakerContentSection
              form={form}
              disabled={isSaving}
              onChange={editor.setField}
            />
            <button type="submit" className="sr-only">
              Guardar
            </button>
          </form>
          {sneaker && (
            <ColorwaysSection
              colorways={sneaker.colorways}
              basePrice={sneaker.base_price}
              totalStock={sneakerStock(sneaker)}
              disabled={isSaving}
              onAdd={editor.addColorway}
              onUpdate={editor.updateColorway}
              onRemove={editor.removeColorway}
              onSetStock={(colorwayId, size, stock) =>
                void editor.setSizeStock(colorwayId, size, stock)
              }
              onRemoveSize={(colorwayId, size) =>
                void editor.removeSize(colorwayId, size)
              }
            />
          )}
        </div>

        <div className="flex flex-col gap-5">
          {sneaker ? (
            <>
              <PublicationPanel
                checks={publishChecks(sneaker)}
                status={sneaker.status}
                disabled={isSaving}
                canChangeStatus={editor.canChangeStatus}
                onChangeStatus={(target) => void editor.changeStatus(target)}
              />
              <PhotosPanel
                images={sneaker.images}
                disabled={isSaving}
                onUpload={(files) => void editor.uploadImages(files)}
                onMakePrimary={(imageId) =>
                  void editor.markPrimaryImage(imageId)
                }
                onRemove={(imageId) => void editor.removeImage(imageId)}
                onMove={(imageId, index) =>
                  void editor.moveImage(imageId, index)
                }
              />
              <SummaryPanel
                stock={sneakerStock(sneaker)}
                colorways={sneaker.colorways.length}
                images={sneaker.images.length}
                updatedAt={sneaker.updated_at}
              />
            </>
          ) : (
            <section className="flex flex-col gap-2 border border-dashed border-border bg-card p-5">
              <h2 className="text-[15px] font-extrabold">
                Colores, tallas y fotos
              </h2>
              <p className="text-[13px] leading-relaxed text-muted-foreground">
                Guarda el borrador para añadir colores, stock por talla y fotos.
                Después podrás publicarlo.
              </p>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
