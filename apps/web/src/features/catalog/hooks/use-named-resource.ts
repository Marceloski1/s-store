import { useEffect, useState } from "react"

import type {
  NamedResourceGateway,
  NamedResourceInput,
  ResourcePage,
} from "@/features/catalog/api/types"
import { toErrorMessage } from "@/lib/api/errors"

const PAGE_SIZE = 10

export function useNamedResource(gateway: NamedResourceGateway) {
  const [page, setPage] = useState(1)
  const [reloadKey, setReloadKey] = useState(0)
  const [data, setData] = useState<ResourcePage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    let ignore = false
    gateway.list(page, PAGE_SIZE).then(
      (result) => {
        if (ignore) return
        setData(result)
        setError(null)
      },
      (reason: unknown) => {
        if (ignore) return
        setError(toErrorMessage(reason))
      }
    )
    return () => {
      ignore = true
    }
  }, [gateway, page, reloadKey])

  async function mutate(action: () => Promise<unknown>): Promise<boolean> {
    setIsSaving(true)
    try {
      await action()
      setError(null)
      setReloadKey((key) => key + 1)
      return true
    } catch (reason) {
      setError(toErrorMessage(reason))
      return false
    } finally {
      setIsSaving(false)
    }
  }

  async function remove(id: string): Promise<boolean> {
    const isLastItemOfPage = data?.items.length === 1 && page > 1
    const removed = await mutate(() => gateway.remove(id))
    if (removed && isLastItemOfPage) {
      setPage((current) => current - 1)
    }
    return removed
  }

  return {
    data,
    error,
    isLoading: data === null && error === null,
    isSaving,
    page,
    setPage,
    create: (input: NamedResourceInput) => mutate(() => gateway.create(input)),
    update: (id: string, input: NamedResourceInput) =>
      mutate(() => gateway.update(id, input)),
    remove,
  }
}
