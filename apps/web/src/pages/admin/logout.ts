import type { APIRoute } from "astro"

import { LOGIN_PATH } from "@/features/auth/api/permissions"
import { authService } from "@/services/admin-services/auth"

const SESSION_COOKIE = "saury_session"

export const POST: APIRoute = async ({ cookies, redirect }) => {
  await authService.logout()
  cookies.delete(SESSION_COOKIE, { path: "/" })
  return redirect(LOGIN_PATH, 303)
}
