import { ApiError } from "@/lib/api/errors"

type FetchResult<T> = {
  data?: T
  error?: unknown
  response: Response
}

export function unwrap<T>(result: FetchResult<T>): T {
  if (result.error !== undefined || result.data === undefined) {
    throw new ApiError(result.error)
  }
  return result.data
}

export function unwrapOrNull<T>(result: FetchResult<T>): T | null {
  if (result.response.status === 404) {
    return null
  }
  return unwrap(result)
}

export function ensureOk(result: FetchResult<unknown>): void {
  if (result.error !== undefined) {
    throw new ApiError(result.error)
  }
}
