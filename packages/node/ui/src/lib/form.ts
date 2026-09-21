import type { ReactNode } from "react"
import type { FieldPath, FieldValues } from "react-hook-form"

import { FormField, type FormFieldProps } from "../components/form"

export function createFormField<TValues extends FieldValues>() {
  return FormField as <TName extends FieldPath<TValues>>(
    props: FormFieldProps<TValues, TName>
  ) => ReactNode
}
