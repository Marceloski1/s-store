import { useRef, useState } from "react"

import {
  adminSneakersGateway,
  formToRequest,
} from "@/features/admin/api/sneakers"
import {
  MAX_IMAGE_BYTES,
  MAX_IMAGES,
  STATUS_TRANSITIONS,
  slugify,
  sneakerToForm,
  type ColorwayInput,
  type SneakerForm,
  type SneakerStatus,
} from "@/features/admin/api/types"
import { toErrorMessage } from "@/lib/api/errors"
import type { ApiSneaker } from "@/lib/api/types"

const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png"]

function editorUrl(slug: string): string {
  return `/admin/sneakers/${slug}`
}

function validateForm(form: SneakerForm): string | null {
  if (!form.name.trim()) return "El nombre del modelo es obligatorio"
  if (!form.brandId || !form.categoryId) {
    return "Elige una marca y una categoría"
  }
  if (form.price.trim() === "" || Number(form.price) < 0) {
    return "Indica un precio base válido"
  }
  const hasQuote = form.testimonialQuote.trim() !== ""
  const hasAuthor = form.testimonialAuthor.trim() !== ""
  if (hasQuote !== hasAuthor) {
    return "El testimonio necesita el texto y quién lo dice, o ninguno de los dos"
  }
  return null
}

export function useSneakerEditor(
  initialSneaker: ApiSneaker | null,
  initialForm: SneakerForm
) {
  const [sneaker, setSneaker] = useState(initialSneaker)
  const [form, setForm] = useState(initialForm)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const latest = useRef(initialSneaker)
  const queue = useRef<Promise<unknown>>(Promise.resolve())
  const pending = useRef(0)

  async function perform(
    action: (current: ApiSneaker) => Promise<ApiSneaker>,
    successMessage: string | null
  ): Promise<ApiSneaker | null> {
    const current = latest.current
    if (!current) return null
    setNotice(null)
    try {
      const updated = await action(current)
      latest.current = updated
      setSneaker(updated)
      setError(null)
      setNotice(successMessage)
      return updated
    } catch (reason) {
      setError(toErrorMessage(reason))
      return null
    }
  }

  function run(
    action: (current: ApiSneaker) => Promise<ApiSneaker>,
    successMessage: string | null = null
  ): Promise<ApiSneaker | null> {
    pending.current += 1
    setIsSaving(true)
    const result = queue.current.then(() => perform(action, successMessage))
    queue.current = result
    return result.finally(() => {
      pending.current -= 1
      if (pending.current === 0) setIsSaving(false)
    })
  }

  function setField<K extends keyof SneakerForm>(
    key: K,
    value: SneakerForm[K]
  ) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  function regenerateSlug() {
    setField("slug", slugify(form.name))
  }

  async function save() {
    const invalid = validateForm(form)
    if (invalid) {
      setError(invalid)
      return
    }
    const request = formToRequest(form)
    if (!sneaker) {
      setIsSaving(true)
      try {
        const created = await adminSneakersGateway.create(request)
        window.location.assign(editorUrl(created.slug))
      } catch (reason) {
        setError(toErrorMessage(reason))
        setIsSaving(false)
      }
      return
    }
    const previousSlug = sneaker.slug
    const updated = await run(
      (current) => adminSneakersGateway.update(current.id, request),
      "Cambios guardados"
    )
    if (!updated) return
    setForm(sneakerToForm(updated))
    if (updated.slug !== previousSlug) {
      window.location.assign(editorUrl(updated.slug))
    }
  }

  function canChangeStatus(target: SneakerStatus): boolean {
    return (
      sneaker !== null &&
      (target === sneaker.status ||
        STATUS_TRANSITIONS[sneaker.status].includes(target))
    )
  }

  async function changeStatus(target: SneakerStatus) {
    if (!sneaker || target === sneaker.status || !canChangeStatus(target)) {
      return
    }
    const transitions = {
      active: adminSneakersGateway.publish,
      archived: adminSneakersGateway.archive,
      draft: adminSneakersGateway.unarchive,
    } satisfies Record<SneakerStatus, (id: string) => Promise<ApiSneaker>>
    const messages: Record<SneakerStatus, string> = {
      active: "Modelo publicado",
      archived: "Modelo archivado",
      draft: "Modelo devuelto a borrador",
    }
    await run((current) => transitions[target](current.id), messages[target])
  }

  function addColorway(input: ColorwayInput) {
    return run(
      (current) => adminSneakersGateway.addColorway(current.id, input),
      "Color añadido"
    )
  }

  function updateColorway(colorwayId: string, input: ColorwayInput) {
    return run(
      (current) =>
        adminSneakersGateway.updateColorway(current.id, colorwayId, input),
      "Color actualizado"
    )
  }

  function removeColorway(colorwayId: string) {
    return run(
      (current) => adminSneakersGateway.removeColorway(current.id, colorwayId),
      "Color eliminado"
    )
  }

  function setSizeStock(colorwayId: string, size: string, stock: number) {
    if (!Number.isInteger(stock) || stock < 0) {
      setError("El stock debe ser un número entero mayor o igual que 0")
      return Promise.resolve(null)
    }
    return run((current) =>
      adminSneakersGateway.setSizeStock(current.id, colorwayId, size, stock)
    )
  }

  function removeSize(colorwayId: string, size: string) {
    return run(
      (current) =>
        adminSneakersGateway.removeSize(current.id, colorwayId, size),
      "Talla eliminada"
    )
  }

  async function uploadImages(files: File[]) {
    if (!sneaker || files.length === 0) return
    const available = MAX_IMAGES - sneaker.images.length
    if (files.length > available) {
      setError(`Solo puedes subir ${available} foto(s) más`)
      return
    }
    const invalid = files.find(
      (file) =>
        !ACCEPTED_IMAGE_TYPES.includes(file.type) || file.size > MAX_IMAGE_BYTES
    )
    if (invalid) {
      setError(`${invalid.name}: solo JPG o PNG de hasta 5 MB`)
      return
    }
    await run(async (current) => {
      let uploaded = current
      for (const file of files) {
        uploaded = await adminSneakersGateway.uploadImage(
          current.id,
          file,
          current.name
        )
      }
      return uploaded
    }, "Fotos subidas")
  }

  function markPrimaryImage(imageId: string) {
    return run((current) =>
      adminSneakersGateway.markPrimaryImage(current.id, imageId)
    )
  }

  function removeImage(imageId: string) {
    return run(
      (current) => adminSneakersGateway.removeImage(current.id, imageId),
      "Foto eliminada"
    )
  }

  function moveImage(imageId: string, targetIndex: number) {
    return run((current) => {
      const ids = current.images.map((image) => image.id)
      const fromIndex = ids.indexOf(imageId)
      if (
        fromIndex === -1 ||
        targetIndex < 0 ||
        targetIndex >= ids.length ||
        targetIndex === fromIndex
      ) {
        return Promise.resolve(current)
      }
      ids.splice(fromIndex, 1)
      ids.splice(targetIndex, 0, imageId)
      return adminSneakersGateway.reorderImages(current.id, ids)
    })
  }

  return {
    sneaker,
    form,
    isSaving,
    error,
    notice,
    setField,
    regenerateSlug,
    save,
    canChangeStatus,
    changeStatus,
    addColorway,
    updateColorway,
    removeColorway,
    setSizeStock,
    removeSize,
    uploadImages,
    markPrimaryImage,
    removeImage,
    moveImage,
  }
}

export type SneakerEditorState = ReturnType<typeof useSneakerEditor>
