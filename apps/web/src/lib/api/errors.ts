const CONNECTION_ERROR_MESSAGE = "No se pudo conectar con la API"
const UNEXPECTED_ERROR_MESSAGE = "Error inesperado"

export class ApiError extends Error {
  constructor(body: unknown) {
    super(detailToMessage(body))
    this.name = "ApiError"
  }
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

function detailToMessage(body: unknown): string {
  if (typeof body !== "object" || body === null || !("detail" in body)) {
    return UNEXPECTED_ERROR_MESSAGE
  }
  const { detail } = body
  if (typeof detail === "string") {
    return detail
  }
  if (Array.isArray(detail)) {
    return detail.map(validationIssueToMessage).join(", ")
  }
  return UNEXPECTED_ERROR_MESSAGE
}

function validationIssueToMessage(issue: unknown): string {
  if (typeof issue === "object" && issue !== null && "msg" in issue) {
    const location =
      "loc" in issue && Array.isArray(issue.loc) ? issue.loc.at(-1) : undefined
    return location
      ? `${String(location)}: ${String(issue.msg)}`
      : String(issue.msg)
  }
  return String(issue)
}
