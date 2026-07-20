import { useCookie, navigateTo } from 'nuxt/app'
import { useRuntimeConfig } from 'nuxt/kit'
import { defineStore } from 'pinia'

interface Utilisateur {
  id: number
  nom: string
  prenom: string
  identifiant: string
  email?: string | null
  role: string
  paroisse_id?: number | null
  locale: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    user: null as Utilisateur | null,
  }),

  getters: {
    estConnecte: (state) => !!state.accessToken,
    role: (state) => state.user?.role ?? null,
  },

  actions: {
    async login(identifiant: string, mot_de_passe: string) {
      const { public: { apiBase } } = useRuntimeConfig()
      const data = await $fetch<{ access_token: string; refresh_token: string }>(
        `${apiBase}/auth/login`,
        { method: 'POST', body: { identifiant, mot_de_passe } }
      )
      this.setTokens(data.access_token, data.refresh_token)
      await this.fetchUser()
    },

    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
      useCookie('emberc_access_token', { maxAge: 60 * 60 }).value = access
      useCookie('emberc_refresh_token', { maxAge: 60 * 60 * 24 * 30 }).value = refresh
    },

    async fetchUser() {
      const { public: { apiBase } } = useRuntimeConfig()
      this.user = await $fetch<Utilisateur>(`${apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${this.accessToken}` },
      })
    },

    async refreshAccessToken() {
      const { public: { apiBase } } = useRuntimeConfig()
      const data = await $fetch<{ access_token: string; refresh_token: string }>(
        `${apiBase}/auth/refresh`,
        { method: 'POST', body: { refresh_token: this.refreshToken } }
      )
      this.setTokens(data.access_token, data.refresh_token)
    },

    hydrateFromCookies() {
      this.accessToken = useCookie<string | null>('emberc_access_token').value
      this.refreshToken = useCookie<string | null>('emberc_refresh_token').value
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      useCookie('emberc_access_token').value = null
      useCookie('emberc_refresh_token').value = null
      navigateTo('/connexion')
    },
  },
})