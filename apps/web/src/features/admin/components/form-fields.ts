import { createFormField } from "@workspace/ui/lib/form"

import type { ColorwayInput, SneakerForm } from "@/features/admin/api/types"

export const SneakerField = createFormField<SneakerForm>()
export const ColorwayField = createFormField<ColorwayInput>()
