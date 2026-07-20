import { useAuthStore } from "~~/stores/auth"

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()

  if (!auth.estConnecte) {
    return navigateTo('/connexion')
  }

  const rolesAutorises = to.meta.rolesAutorises as string[] | undefined
  if (rolesAutorises && !rolesAutorises.includes(auth.role ?? '')) {
    return navigateTo('/')
  }
})