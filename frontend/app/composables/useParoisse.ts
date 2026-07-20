interface Paroisse {
  id: number
  nom: string
}

export function useParoisses() {
  const { request } = useApi()

  const { data: paroisses, pending } = useAsyncData(
    'paroisses-selecteur',
    () => request<Paroisse[]>('/paroisses?limit=100')
  )

  return { paroisses, pending }
}