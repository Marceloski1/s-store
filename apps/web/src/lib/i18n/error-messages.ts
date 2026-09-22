import { ErrorCode, Role, SneakerStatus } from "@/lib/api/types"
import { toEnum } from "@/lib/enums"
import {
  fieldLabel,
  ROLE_LABELS,
  SNEAKER_STATUS_LABELS,
} from "@/lib/i18n/labels"

export type ErrorParams = Partial<Record<string, string | number>>

type ErrorTranslator = (params: ErrorParams) => string

function status(value: string | number | undefined): string {
  const parsed = toEnum(SneakerStatus, String(value ?? ""))
  return parsed ? SNEAKER_STATUS_LABELS[parsed] : String(value ?? "")
}

function role(value: string | number | undefined): string {
  const parsed = toEnum(Role, String(value ?? ""))
  return parsed ? ROLE_LABELS[parsed] : String(value ?? "")
}

const IMAGE_INVALID_REASONS: Partial<Record<string, string>> = {
  UNSUPPORTED_TYPE: "solo se aceptan fotos JPG o PNG",
  EMPTY: "el archivo está vacío",
  TOO_LARGE: "la foto supera los 5 MB",
  CONTENT_MISMATCH: "el contenido no corresponde a una imagen válida",
}

const CANNOT_MANAGE_USER_REASONS: Partial<Record<string, string>> = {
  SUPER_ADMIN: "no se puede modificar a un superadministrador",
  SELF: "no puedes eliminar tu propia cuenta",
}

export const ERROR_MESSAGES: Record<ErrorCode, ErrorTranslator> = {
  [ErrorCode.VALIDATION_ERROR]: () => "Revisa los datos del formulario",
  [ErrorCode.NOT_FOUND]: () => "No se encontró lo que buscas",
  [ErrorCode.CONFLICT]: () => "La operación entra en conflicto con otro dato",
  [ErrorCode.UNAUTHORIZED]: () => "Tu sesión no es válida; vuelve a entrar",
  [ErrorCode.FORBIDDEN]: () => "No tienes permiso para esta acción",
  [ErrorCode.EXTERNAL_SERVICE_ERROR]: () =>
    "Un servicio externo no respondió; inténtalo de nuevo",
  [ErrorCode.HTTP_ERROR]: () => "La petición no se pudo completar",
  [ErrorCode.INTERNAL_ERROR]: () => "Error interno del servidor",
  [ErrorCode.TEXT_REQUIRED]: (p) =>
    `El campo ${fieldLabel(p.field)} es obligatorio`,
  [ErrorCode.TEXT_TOO_LONG]: (p) =>
    `El campo ${fieldLabel(p.field)} admite como máximo ${p.max} caracteres`,
  [ErrorCode.INVALID_SLUG]: (p) =>
    `El slug «${p.value}» solo puede tener minúsculas, números y guiones`,
  [ErrorCode.INVALID_CURRENCY]: (p) => `La moneda «${p.currency}» no es válida`,
  [ErrorCode.INVALID_AMOUNT]: (p) => `El importe «${p.value}» no es válido`,
  [ErrorCode.NEGATIVE_AMOUNT]: () => "El importe no puede ser negativo",
  [ErrorCode.AMOUNT_TOO_LARGE]: (p) => `El importe no puede superar ${p.max}`,
  [ErrorCode.TOO_MANY_DECIMALS]: (p) =>
    `El importe admite como máximo ${p.max} decimales`,
  [ErrorCode.MONEY_CURRENCY_MISMATCH]: (p) =>
    `No se pueden combinar importes en ${p.expected} y ${p.actual}`,
  [ErrorCode.INVALID_PAGE]: () => "La página indicada no es válida",
  [ErrorCode.INVALID_PAGE_SIZE]: (p) =>
    `El tamaño de página debe estar entre 1 y ${p.max}`,
  [ErrorCode.BRAND_NOT_FOUND]: () => "La marca no existe",
  [ErrorCode.BRAND_SLUG_ALREADY_EXISTS]: (p) =>
    `Ya existe una marca con el slug «${p.slug}»`,
  [ErrorCode.BRAND_IN_USE]: () =>
    "La marca tiene sneakers asociados y no se puede borrar",
  [ErrorCode.CATEGORY_NOT_FOUND]: () => "La categoría no existe",
  [ErrorCode.CATEGORY_SLUG_ALREADY_EXISTS]: (p) =>
    `Ya existe una categoría con el slug «${p.slug}»`,
  [ErrorCode.CATEGORY_IN_USE]: () =>
    "La categoría tiene sneakers asociados y no se puede borrar",
  [ErrorCode.SNEAKER_NOT_FOUND]: () => "El modelo no existe",
  [ErrorCode.SNEAKER_SLUG_ALREADY_EXISTS]: (p) =>
    `Ya existe un modelo con el slug «${p.slug}»`,
  [ErrorCode.SNEAKER_REFERENCE_ALREADY_EXISTS]: (p) =>
    `Ya existe un modelo con la referencia «${p.reference}»`,
  [ErrorCode.SNEAKER_NEEDS_PRIMARY_IMAGE]: () =>
    "Para publicar el modelo necesita una foto principal",
  [ErrorCode.SNEAKER_NEEDS_SIZED_COLORWAY]: () =>
    "Para publicar el modelo necesita al menos un color con tallas",
  [ErrorCode.INVALID_STATUS_TRANSITION]: (p) =>
    `No se puede pasar de «${status(p.from)}» a «${status(p.to)}»`,
  [ErrorCode.COLORWAY_NOT_FOUND]: () => "El color no existe",
  [ErrorCode.SKU_ALREADY_EXISTS]: (p) => `El SKU «${p.sku}» ya está en uso`,
  [ErrorCode.SIZE_NOT_FOUND]: (p) =>
    `La talla ${p.size} no existe en este color`,
  [ErrorCode.IMAGE_NOT_FOUND]: () => "La foto no existe",
  [ErrorCode.IMAGE_LIMIT_EXCEEDED]: (p) =>
    `Un modelo admite como máximo ${p.limit} fotos`,
  [ErrorCode.IMAGE_INVALID]: (p) =>
    `Foto no válida: ${IMAGE_INVALID_REASONS[String(p.reason)] ?? "formato no admitido"}`,
  [ErrorCode.IMAGE_STORAGE_ERROR]: () =>
    "No se pudo guardar la foto en el almacenamiento; inténtalo de nuevo",
  [ErrorCode.INVALID_IMAGE_ORDER]: () =>
    "El nuevo orden debe incluir todas las fotos una sola vez",
  [ErrorCode.INVALID_IMAGE_POSITION]: () =>
    "La posición de la foto no es válida",
  [ErrorCode.CURRENCY_MISMATCH]: (p) =>
    `El precio debe estar en ${p.expected}, no en ${p.actual}`,
  [ErrorCode.CURRENCY_REQUIRED]: () =>
    "Indica la moneda para filtrar por precio",
  [ErrorCode.INVALID_PRICE_RANGE]: () =>
    "El precio mínimo no puede ser mayor que el máximo",
  [ErrorCode.INVALID_OPTION]: (p) =>
    `«${p.value}» no es una opción válida para ${fieldLabel(p.field)}`,
  [ErrorCode.INVALID_SKU]: (p) =>
    `El SKU «${p.value}» solo admite letras, números y guiones (máximo ${p.max})`,
  [ErrorCode.INVALID_COLOR_CODE]: (p) =>
    `El color «${p.value}» debe tener el formato #RRGGBB`,
  [ErrorCode.INVALID_SHOE_SIZE]: (p) =>
    `La talla «${p.value}» debe ser EU, positiva, en pasos de 0,5 y hasta ${p.max}`,
  [ErrorCode.INVALID_REFERENCE]: (p) =>
    `La referencia «${p.value}» solo admite letras, números y guiones (máximo ${p.max})`,
  [ErrorCode.NEGATIVE_STOCK]: () => "El stock no puede ser negativo",
  [ErrorCode.USER_NOT_FOUND]: () => "El usuario no existe",
  [ErrorCode.EMAIL_ALREADY_EXISTS]: (p) =>
    `Ya existe un usuario con el correo ${p.email}`,
  [ErrorCode.INVALID_CREDENTIALS]: () => "Correo o contraseña incorrectos",
  [ErrorCode.INACTIVE_USER]: () =>
    "Tu cuenta está desactivada; habla con un superadministrador",
  [ErrorCode.NOT_AUTHENTICATED]: () => "Inicia sesión para continuar",
  [ErrorCode.INSUFFICIENT_ROLE]: (p) =>
    `Esta acción requiere el rol ${role(p.role)}`,
  [ErrorCode.CANNOT_MANAGE_USER]: (p) =>
    CANNOT_MANAGE_USER_REASONS[String(p.reason)] ??
    "No se puede gestionar este usuario",
  [ErrorCode.INVALID_EMAIL]: (p) => `El correo «${p.value}» no es válido`,
  [ErrorCode.PASSWORD_TOO_SHORT]: (p) =>
    `La contraseña debe tener al menos ${p.min} caracteres`,
  [ErrorCode.PASSWORD_TOO_LONG]: (p) =>
    `La contraseña admite como máximo ${p.max} caracteres`,
}

type FieldErrorTranslator = (ctx: ErrorParams) => string

export const VALIDATION_TYPE_MESSAGES: Partial<
  Record<string, FieldErrorTranslator>
> = {
  missing: () => "es obligatorio",
  string_too_short: (ctx) =>
    ctx.min_length === 1
      ? "es obligatorio"
      : `mínimo ${ctx.min_length} caracteres`,
  string_too_long: (ctx) => `máximo ${ctx.max_length} caracteres`,
  string_pattern_mismatch: () => "tiene un formato no válido",
  string_type: () => "debe ser un texto",
  enum: (ctx) => `debe ser uno de: ${ctx.expected}`,
  literal_error: (ctx) => `debe ser uno de: ${ctx.expected}`,
  greater_than_equal: (ctx) => `debe ser mayor o igual que ${ctx.ge}`,
  greater_than: (ctx) => `debe ser mayor que ${ctx.gt}`,
  less_than_equal: (ctx) => `debe ser menor o igual que ${ctx.le}`,
  less_than: (ctx) => `debe ser menor que ${ctx.lt}`,
  decimal_parsing: () => "debe ser un número",
  decimal_max_places: (ctx) =>
    `admite como máximo ${ctx.decimal_places} decimales`,
  int_parsing: () => "debe ser un número entero",
  float_parsing: () => "debe ser un número",
  bool_parsing: () => "debe ser verdadero o falso",
  date_from_datetime_parsing: () => "debe ser una fecha válida",
  date_parsing: () => "debe ser una fecha válida",
  uuid_parsing: () => "no es un identificador válido",
  json_invalid: () => "el formato de la petición no es válido",
}

export function fieldErrorMessage(
  field: string,
  type: string,
  ctx: ErrorParams
): string {
  const describe = VALIDATION_TYPE_MESSAGES[type]
  return `${fieldLabel(field)}: ${describe ? describe(ctx) : "no es válido"}`
}
