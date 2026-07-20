import { useAuthStore } from "../../stores/auth"

export function useApi() {
  const { public: { apiBase } } = useRuntimeConfig()
  const auth = useAuthStore()

  async function request<T>(path: string, options: any = {}): Promise<T> {
    const doFetch = (token: string | null) =>
      $fetch<T>(`${apiBase}${path}`, {
        ...options,
        headers: {
          ...(options.headers || {}),
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      })

    try {
      return await doFetch(auth.accessToken)
    } catch (error: any) {
      if (error?.response?.status === 401 && auth.refreshToken) {
        await auth.refreshAccessToken()
        return await doFetch(auth.accessToken)
      }
      throw error
    }
  }

  return { request }
}

