export function toEnum<E extends Record<string, string>>(
  enumObject: E,
  value: string | null | undefined
): E[keyof E] | null {
  const normalized = value?.trim().toUpperCase()
  const match = Object.values(enumObject).find((item) => item === normalized)
  return (match as E[keyof E] | undefined) ?? null
}

export function toEnums<E extends Record<string, string>>(
  enumObject: E,
  values: string[]
): E[keyof E][] {
  return values
    .map((value) => toEnum(enumObject, value))
    .filter((value): value is E[keyof E] => value !== null)
}
