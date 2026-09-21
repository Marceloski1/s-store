import { AsyncLocalStorage } from "node:async_hooks"

import { API_URL } from "astro:env/server"

import { apiClient, SERVER_API_ORIGIN } from "@/lib/api/client"

type RequestContext = {
  cookie: string | null
}

const requestContext = new AsyncLocalStorage<RequestContext>()

let installed = false

function installServerMiddleware() {
  if (installed) return
  installed = true
  apiClient.use({
    onRequest({ request }) {
      const target = request.url.replace(
        SERVER_API_ORIGIN,
        API_URL.replace(/\/$/, "")
      )
      const headers = new Headers(request.headers)
      const cookie = requestContext.getStore()?.cookie
      if (cookie) headers.set("cookie", cookie)
      return new Request(target, {
        method: request.method,
        headers,
        body: request.body,
        duplex: "half",
      } as RequestInit)
    },
  })
}

export function withRequestCookie<T>(
  cookie: string | null,
  callback: () => T
): T {
  installServerMiddleware()
  return requestContext.run({ cookie }, callback)
}
