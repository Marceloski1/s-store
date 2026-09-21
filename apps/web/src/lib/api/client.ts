import createClient from "openapi-fetch"

import type { paths } from "@/lib/api/schema"

export const API_PROXY_PATH = "/api"
export const SERVER_API_ORIGIN = "http://sauri-api.server"

export const apiClient = createClient<paths>({
  baseUrl: import.meta.env.SSR ? SERVER_API_ORIGIN : API_PROXY_PATH,
})
