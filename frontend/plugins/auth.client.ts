import { defineNuxtPlugin } from "nuxt/app"
import { useAuthStore } from "../stores/auth"

export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  auth.hydrateFromCookies()
  if (auth.accessToken && !auth.user) {
    try {
      await auth.fetchUser()
    } catch {
      auth.logout()
    }
  }
})