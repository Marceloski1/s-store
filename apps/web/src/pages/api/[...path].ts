import type { APIRoute } from "astro"
import { API_URL } from "astro:env/server"

const HOP_BY_HOP_HEADERS = [
  "connection",
  "content-encoding",
  "content-length",
  "host",
  "keep-alive",
  "transfer-encoding",
]

function forwardableHeaders(source: Headers): Headers {
  const headers = new Headers(source)
  for (const name of HOP_BY_HOP_HEADERS) headers.delete(name)
  return headers
}

export const ALL: APIRoute = async ({ request, params, url }) => {
  const target = new URL(
    `${params.path ?? ""}${url.search}`,
    `${API_URL.replace(/\/$/, "")}/`
  )
  const hasBody = !["GET", "HEAD"].includes(request.method)
  const response = await fetch(target, {
    method: request.method,
    headers: forwardableHeaders(request.headers),
    body: hasBody ? await request.arrayBuffer() : undefined,
    redirect: "manual",
  })
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: forwardableHeaders(response.headers),
  })
}
