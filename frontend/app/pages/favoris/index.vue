<template>
  <div>
    <p class="section-label mb-2">Mon espace</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Mes favoris</h1>

    <div class="flex flex-wrap items-center gap-2 mb-6">
      <button
        v-for="option in types"
        :key="option.value ?? 'tous'"
        class="px-3 py-1.5 rounded-full text-sm border transition"
        :class="typeActif === option.value
          ? 'bg-primary text-white border-primary'
          : 'border-ink/15 text-muted hover:border-primary/40 hover:text-primary'"
        @click="typeActif = option.value"
      >
        {{ option.label }}
      </button>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement de vos favoris...</div>
    <div v-else-if="!elementsAffiches.length" class="text-muted text-sm">
      Aucun favori pour l'instant.
    </div>

    <div v-else class="flex flex-col gap-3">
      <div
        v-for="item in elementsAffiches"
        :key="`${item.type}-${item.id}`"
        class="bg-surface border border-ink/10 rounded-lg p-4 flex items-start justify-between gap-3"
      >
        <div>
          <span class="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary mb-1 inline-block">
            {{ libelleType(item.type) }}
          </span>
          <NuxtLink v-if="item.lien" :to="item.lien" class="block font-medium hover:underline">
            {{ item.titre }}
          </NuxtLink>
          <p v-else class="font-medium">{{ item.titre }}</p>
        </div>
        <BoutonFavori :type="item.type" :item-id="item.id" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

type TypeFavori = 'annonce' | 'evenement' | 'media' | 'chant' | 'article'

interface ElementFavori {
  type: TypeFavori
  id: number
  titre: string
  lien?: string
}

const types = [
  { value: null, label: 'Tous' },
  { value: 'chant' as TypeFavori, label: 'Chants' },
  { value: 'media' as TypeFavori, label: 'Médias' },
  { value: 'evenement' as TypeFavori, label: 'Événements' },
  { value: 'annonce' as TypeFavori, label: 'Annonces' },
  { value: 'article' as TypeFavori, label: 'Actualités' },
]

function libelleType(valeur: TypeFavori) {
  return types.find((t) => t.value === valeur)?.label ?? valeur
}

const { request } = useApi()
const { favoris, chargerFavoris } = useFavoris()
const typeActif = ref<TypeFavori | null>(null)
const pending = ref(true)
const elements = ref<ElementFavori[]>([])

async function chargerDetail(type: TypeFavori, itemId: number): Promise<ElementFavori | null> {
  try {
    if (type === 'chant') {
      const c = await request<{ id: number; titre: string; numero: string }>(`/chants/${itemId}`)
      return { type, id: itemId, titre: `${c.numero} — ${c.titre}`, lien: `/chants/${itemId}` }
    }
    if (type === 'media') {
      const m = await request<{ id: number; titre: string }>(`/medias/${itemId}`)
      return { type, id: itemId, titre: m.titre, lien: '/medias' }
    }
    if (type === 'evenement') {
      const e = await request<{ id: number; titre: string }>(`/evenements/${itemId}`)
      return { type, id: itemId, titre: e.titre, lien: '/evenements' }
    }
    if (type === 'annonce') {
      const a = await request<{ id: number; titre: string }>(`/annonces/${itemId}`)
      return { type, id: itemId, titre: a.titre, lien: '/annonces' }
    }
    if (type === 'article') {
      const art = await request<{ id: number; titre: string }>(`/actualites/${itemId}`)
      return { type, id: itemId, titre: art.titre, lien: `/actualites/${itemId}` }
    }
    return null
  } catch {
    // L'élément a peut-être été supprimé depuis — on l'ignore silencieusement dans la liste
    return null
  }
}

async function chargerTout() {
  pending.value = true
  await chargerFavoris()
  const resultats = await Promise.all(
    favoris.value.map((f) => chargerDetail(f.type_favoris, f.item_id))
  )
  elements.value = resultats.filter((e): e is ElementFavori => e !== null)
  pending.value = false
}

const elementsAffiches = computed(() =>
  typeActif.value ? elements.value.filter((e) => e.type === typeActif.value) : elements.value
)

await chargerTout()
</script>