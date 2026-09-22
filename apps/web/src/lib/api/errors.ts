import { ErrorCode } from "@/lib/api/types"
import { toEnum } from "@/lib/enums"
import {
  ERROR_MESSAGES,
  fieldErrorMessage,
  type ErrorParams,
} from "@/lib/i18n/error-messages"

const CONNECTION_ERROR_MESSAGE = "No se pudo conectar con la API"
const UNEXPECTED_ERROR_MESSAGE = "Error inesperado"

export type ApiFieldError = {
  field: string
  type: string
  ctx: ErrorParams
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null
}

function toParams(value: unknown): ErrorParams {
  if (!isRecord(value)) return {}
  return Object.fromEntries(
    Object.entries(value).filter(
      (entry): entry is [string, string | number] =>
        typeof entry[1] === "string" || typeof entry[1] === "number"
    )
  )
}

function toFieldErrors(value: unknown): ApiFieldError[] {
  if (!Array.isArray(value)) return []
  return value.filter(isRecord).map((item) => ({
    field: String(item.field ?? ""),
    type: String(item.type ?? ""),
    ctx: toParams(item.ctx),
  }))
}

export class ApiError extends Error {
  readonly code: ErrorCode | null
  readonly params: ErrorParams
  readonly fieldErrors: ApiFieldError[]

  constructor(body: unknown) {
    const record = isRecord(body) ? body : {}
    const code = toEnum(ErrorCode, String(record.code ?? ""))
    const params = toParams(record.params)
    const fieldErrors = toFieldErrors(record.errors)
    super(translate(code, params, fieldErrors))
    this.name = "ApiError"
    this.code = code
    this.params = params
    this.fieldErrors = fieldErrors
  }
}

function translate(
  code: ErrorCode | null,
  params: ErrorParams,
  fieldErrors: ApiFieldError[]
): string {
  if (fieldErrors.length > 0) {
    return fieldErrors
      .map((error) => fieldErrorMessage(error.field, error.type, error.ctx))
      .join(" · ")
  }
  return code ? ERROR_MESSAGES[code](params) : UNEXPECTED_ERROR_MESSAGE
}

export function toErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }
  if (error instanceof TypeError) {
    return CONNECTION_ERROR_MESSAGE
  }
  return UNEXPECTED_ERROR_MESSAGE
}
