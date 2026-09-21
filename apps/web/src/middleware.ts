import { defineMiddleware } from "astro:middleware"

import {
  isAdminPath,
  resolveAdminRedirect,
} from "@/features/auth/api/permissions"
import { withRequestCookie } from "@/lib/api/server-context"
import { authService } from "@/services/admin-services/auth"

export const onRequest = defineMiddleware((context, next) =>
  withRequestCookie(context.request.headers.get("cookie"), async () => {
    context.locals.user = null
    const path = context.url.pathname
    if (!isAdminPath(path)) return next()
    context.locals.user = await authService.me()
    const redirect = resolveAdminRedirect(
      path,
      context.url.search,
      context.locals.user
    )
    return redirect ? context.redirect(redirect) : next()
  })
)
