import { useAuthStore } from "~~/stores/auth"

export type TypeFavori = 'annonce' | 'evenement' | 'media' | 'chant' | 'article'

interface Favori {
  id: number
  user_id: number
  type_favoris: TypeFavori
  item_id: number
  created_at: string
}

export function useFavoris() {
  const { request } = useApi()
  const auth = useAuthStore()

  const favoris = useState<Favori[]>('favoris-liste', () => [])
  const charge = useState<boolean>('favoris-charge', () => false)

  async function chargerFavoris() {
    if (!auth.estConnecte) {
      favoris.value = []
      return
    }
    favoris.value = await request<Favori[]>('/favoris')
    charge.value = true
  }

  function estFavori(type: TypeFavori, itemId: number) {
    return favoris.value.some((f) => f.type_favoris === type && f.item_id === itemId)
  }

  function favoriId(type: TypeFavori, itemId: number) {
    return favoris.value.find((f) => f.type_favoris === type && f.item_id === itemId)?.id ?? null
  }

  async function basculerFavori(type: TypeFavori, itemId: number) {
    const existant = favoriId(type, itemId)
    if (existant) {
      await request(`/favoris/${existant}`, { method: 'DELETE' })
      favoris.value = favoris.value.filter((f) => f.id !== existant)
    } else {
      const nouveau = await request<Favori>('/favoris', {
        method: 'POST',
        body: { type_favoris: type, item_id: itemId },
      })
      favoris.value = [...favoris.value, nouveau]
    }
  }

  return { favoris, charge, chargerFavoris, estFavori, basculerFavori }
}

export function resetFavoris() {
  useState<Favori[]>('favoris-liste').value = []
  useState<boolean>('favoris-charge').value = false
}