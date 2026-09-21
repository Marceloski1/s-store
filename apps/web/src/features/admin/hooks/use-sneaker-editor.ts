import { useRef, useState } from "react"

import type { FormApi } from "@workspace/ui/components/form"

import { colorwayRequest, formToRequest } from "@/features/admin/api/sneakers"
import {
  MAX_IMAGE_BYTES,
  MAX_IMAGES,
  STATUS_TRANSITIONS,
  slugify,
  sneakerToForm,
  type ColorwayInput,
  type SneakerForm,
  SneakerStatus,
} from "@/features/admin/api/types"
import { toErrorMessage } from "@/lib/api/errors"
import { colorwayService } from "@/services/admin-services/colorway"
import { imageService } from "@/services/admin-services/image"
import { sneakerService } from "@/services/admin-services/sneaker"
import type { ApiSneaker } from "@/lib/api/types"

const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png"]

function editorUrl(slug: string): string {
  return `/admin/sneakers/${slug}`
}

export function useSneakerEditor(initialSneaker: ApiSneaker | null) {
  const [sneaker, setSneaker] = useState(initialSneaker)
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

  async function save(values: SneakerForm, form: FormApi<SneakerForm>) {
    const request = formToRequest(values)
    if (!sneaker) {
      setIsSaving(true)
      try {
        const created = await sneakerService.create(request)
        window.location.assign(editorUrl(created.slug))
      } catch (reason) {
        setError(toErrorMessage(reason))
        setIsSaving(false)
      }
      return
    }
    const previousSlug = sneaker.slug
    const updated = await run(
      (current) => sneakerService.update(current.id, request),
      "Cambios guardados"
    )
    if (!updated) return
    form.reset(sneakerToForm(updated))
    if (updated.slug !== previousSlug) {
      window.location.assign(editorUrl(updated.slug))
    }
  }

  function regenerateSlug(form: FormApi<SneakerForm>) {
    form.setValue("slug", slugify(form.getValues("name")), {
      shouldValidate: true,
      shouldDirty: true,
    })
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
      [SneakerStatus.ACTIVE]: sneakerService.publish,
      [SneakerStatus.ARCHIVED]: sneakerService.archive,
      [SneakerStatus.DRAFT]: sneakerService.unarchive,
    } satisfies Record<SneakerStatus, (id: string) => Promise<ApiSneaker>>
    const messages: Record<SneakerStatus, string> = {
      [SneakerStatus.ACTIVE]: "Modelo publicado",
      [SneakerStatus.ARCHIVED]: "Modelo archivado",
      [SneakerStatus.DRAFT]: "Modelo devuelto a borrador",
    }
    await run((current) => transitions[target](current.id), messages[target])
  }

  function addColorway(input: ColorwayInput) {
    return run(
      (current) => colorwayService.add(current.id, colorwayRequest(input)),
      "Color añadido"
    )
  }

  function updateColorway(colorwayId: string, input: ColorwayInput) {
    return run(
      (current) =>
        colorwayService.update(current.id, colorwayId, colorwayRequest(input)),
      "Color actualizado"
    )
  }

  function removeColorway(colorwayId: string) {
    return run(
      (current) => colorwayService.remove(current.id, colorwayId),
      "Color eliminado"
    )
  }

  function setSizeStock(colorwayId: string, size: string, stock: number) {
    if (!Number.isInteger(stock) || stock < 0) {
      setError("El stock debe ser un número entero mayor o igual que 0")
      return Promise.resolve(null)
    }
    return run((current) =>
      colorwayService.setSizeStock(current.id, colorwayId, size, stock)
    )
  }

  function removeSize(colorwayId: string, size: string) {
    return run(
      (current) => colorwayService.removeSize(current.id, colorwayId, size),
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
        uploaded = await imageService.upload(current.id, file, current.name)
      }
      return uploaded
    }, "Fotos subidas")
  }

  function markPrimaryImage(imageId: string) {
    return run((current) => imageService.markPrimary(current.id, imageId))
  }

  function removeImage(imageId: string) {
    return run(
      (current) => imageService.remove(current.id, imageId),
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
      return imageService.reorder(current.id, ids)
    })
  }

  return {
    sneaker,
    isSaving,
    error,
    notice,
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
