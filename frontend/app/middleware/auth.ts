import { defineNuxtRouteMiddleware, navigateTo } from "nuxt/app"
import { useAuthStore } from "../stores/auth"

export default defineNuxtRouteMiddleware(() => {
  const auth = useAuthStore()
  if (!auth.estConnecte) {
    return navigateTo('/connexion')
  }
})