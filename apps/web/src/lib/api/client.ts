import { PUBLIC_API_URL } from "astro:env/client"
import createClient from "openapi-fetch"

import type { paths } from "@/lib/api/schema"

export const apiClient = createClient<paths>({ baseUrl: PUBLIC_API_URL })
