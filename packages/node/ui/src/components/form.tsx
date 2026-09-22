import * as React from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { cn } from "cn"
import {
  FormProvider,
  useController,
  useForm,
  useFormContext,
  type ControllerFieldState,
  type ControllerRenderProps,
  type DefaultValues,
  type FieldPath,
  type FieldValues,
  type UseFormReturn,
} from "react-hook-form"
import type { z } from "zod"

type FormApi<
  TInput extends FieldValues,
  TOutput extends FieldValues = TInput,
> = UseFormReturn<TInput, unknown, TOutput>

type FormProps<TInput extends FieldValues, TOutput extends FieldValues> = Omit<
  React.ComponentProps<"form">,
  "onSubmit" | "children"
> & {
  schema: z.ZodType<TOutput, TInput>
  defaultValues: DefaultValues<TInput>
  disabled?: boolean
  onSubmit: (
    values: TOutput,
    form: FormApi<TInput, TOutput>
  ) => void | Promise<void>
  children:
    | React.ReactNode
    | ((form: FormApi<TInput, TOutput>) => React.ReactNode)
}

function Form<TInput extends FieldValues, TOutput extends FieldValues>({
  schema,
  defaultValues,
  disabled,
  onSubmit,
  children,
  ...props
}: FormProps<TInput, TOutput>) {
  const form = useForm<TInput, unknown, TOutput>({
    resolver: zodResolver<TInput, unknown, TOutput>(schema),
    defaultValues,
    disabled,
    mode: "onChange",
  })

  return (
    <FormProvider {...form}>
      <form
        method="post"
        noValidate
        data-slot="form"
        onSubmit={form.handleSubmit((values) => onSubmit(values, form))}
        {...props}
      >
        {typeof children === "function" ? children(form) : children}
      </form>
    </FormProvider>
  )
}

type FormControlProps = {
  id: string
  "aria-invalid": boolean
  "aria-describedby"?: string
}

type FormFieldProps<
  TValues extends FieldValues,
  TName extends FieldPath<TValues>,
> = {
  name: TName
  id?: string
  label?: React.ReactNode
  description?: React.ReactNode
  className?: string
  labelClassName?: string
  messageClassName?: string
  render: (props: {
    field: ControllerRenderProps<TValues, TName>
    fieldState: ControllerFieldState
    control: FormControlProps
  }) => React.ReactNode
}

function FormField<
  TValues extends FieldValues = FieldValues,
  TName extends FieldPath<TValues> = FieldPath<TValues>,
>({
  name,
  id,
  label,
  description,
  className,
  labelClassName,
  messageClassName,
  render,
}: FormFieldProps<TValues, TName>) {
  const generatedId = React.useId()
  const controlId = id ?? generatedId
  const { control } = useFormContext<TValues>()
  const { field, fieldState } = useController({ name, control })
  const message = fieldState.error?.message
  const messageId = `${controlId}-message`
  const descriptionId = `${controlId}-description`

  return (
    <div
      data-slot="form-field"
      className={cn("flex flex-col gap-1.5", className)}
    >
      {label && (
        <label
          htmlFor={controlId}
          className={labelClassName ?? "text-xs font-medium"}
        >
          {label}
        </label>
      )}
      {render({
        field,
        fieldState,
        control: {
          id: controlId,
          "aria-invalid": Boolean(message),
          "aria-describedby": message
            ? messageId
            : description
              ? descriptionId
              : undefined,
        },
      })}
      {message ? (
        <p
          id={messageId}
          role="alert"
          className={
            messageClassName ?? "text-[11px] font-semibold text-destructive"
          }
        >
          {message}
        </p>
      ) : (
        description && (
          <p id={descriptionId} className="text-[11px] text-muted-foreground">
            {description}
          </p>
        )
      )}
    </div>
  )
}

export { Form, FormField }
export type { FormApi, FormControlProps, FormFieldProps }
