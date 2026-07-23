<template>
  <div>
    <p class="section-label mb-2">Bibliothèque</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Chants</h1>

    <div class="flex flex-wrap items-center gap-2 mb-6">
      <button
        v-for="option in categories"
        :key="option.value"
        class="px-3 py-1.5 rounded-full text-sm border transition"
        :class="categorieActive === option.value
          ? 'bg-primary text-white border-primary'
          : 'border-ink/15 text-muted hover:border-primary/40 hover:text-primary'"
        @click="basculerCategorie(option.value)"
      >
        {{ option.label }}
      </button>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement des chants...</div>

    <div v-else-if="error" class="text-sm text-red-600">
      Impossible de charger les chants pour le moment.
    </div>

    <div v-else-if="!chantsAffiches.length" class="text-muted text-sm">
      Aucun chant ne correspond à cette catégorie pour l'instant.
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <article
        v-for="chant in chantsAffiches"
        :key="chant.id"
        class="bg-surface border border-ink/10 rounded-lg p-5 flex flex-col gap-3"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <p class="text-xs text-muted mb-1">N° {{ chant.numero }}</p>
            <h2 class="font-display text-lg font-semibold leading-snug">{{ chant.titre }}</h2>
          </div>
          <span class="text-xs px-2 py-1 rounded-full bg-accent/15 text-accent-dark whitespace-nowrap">
            {{ libelleCategorie(chant.categorie) }}
          </span>
        </div>

        <p v-if="chant.auteur" class="text-sm text-muted">{{ chant.auteur }}</p>
        <BoutonFavori type="chant" :item-id="chant.id" avec-label />

        <audio
          v-if="chant.fichier_audio_url"
          :src="chant.fichier_audio_url"
          controls
          class="w-full mt-1"
        />

        <NuxtLink
          :to="`/chants/${chant.id}`"
          class="text-sm font-medium text-primary hover:underline mt-auto"
        >
          Voir les paroles →
        </NuxtLink>
      </article>
    </div>

    <div class="flex items-center justify-between mt-8" v-if="!pending && chantsAffiches.length">
      <button
        class="text-sm font-medium text-primary disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="page === 1"
        @click="page--"
      >
        ← Précédent
      </button>
      <span class="text-sm text-muted">Page {{ page }}</span>
      <button
        class="text-sm font-medium text-primary disabled:opacity-40 disabled:cursor-not-allowed"
        :disabled="chantsAffiches.length < limit"
        @click="page++"
      >
        Suivant →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Chant {
  id: number
  numero: string
  titre: string
  paroles?: string | null
  categorie: string
  auteur?: string | null
  fichier_audio_url?: string | null
}

const categories = [
  { value: null, label: 'Tous' },
  { value: 'chant', label: 'Chant' },
  { value: 'chant_de_messe', label: 'Chant de messe' },
  { value: 'chant_de_la_saintete', label: 'Sainteté' },
  { value: 'chant_de_la_vie', label: 'Vie' },
  { value: 'chant_de_la_paix', label: 'Paix' },
  { value: 'chant_de_la_joie', label: 'Joie' },
]

function libelleCategorie(valeur: string) {
  return categories.find((c) => c.value === valeur)?.label ?? valeur
}

const { request } = useApi()
const page = ref(1)
const limit = 12
const categorieActive = ref<string | null>(null)

function basculerCategorie(valeur: string | null) {
  categorieActive.value = valeur
  page.value = 1
}

const { data: chants, pending, error } = await useAsyncData(
  'chants-liste',
  () => request<Chant[]>(`/chants?page=${page.value}&limit=${limit}`),
  { watch: [page] }
)

const chantsAffiches = computed(() => {
  const liste = chants.value ?? []
  if (!categorieActive.value) return liste
  return liste.filter((c) => c.categorie === categorieActive.value)
})
</script>