<template>
  <div>
    <p class="section-label mb-2">Vie de l'église</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Annonces</h1>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement des annonces...</div>

    <div v-else-if="error" class="text-sm text-red-600">
      Impossible de charger les annonces pour le moment.
    </div>

    <div v-else-if="!annonces?.length" class="text-muted text-sm">
      Aucune annonce active pour le moment.
    </div>

    <div v-else class="flex flex-col gap-4">
      <article
        v-for="annonce in annoncesTriees"
        :key="annonce.id"
        class="bg-surface border rounded-lg p-5"
        :class="annonce.important ? 'border-accent/50 ring-1 ring-accent/20' : 'border-ink/10'"
      >
        <div class="flex items-start justify-between gap-3 mb-2">
          <h2 class="font-display text-lg font-semibold">{{ annonce.titre }}</h2>
          <span
            v-if="annonce.important"
            class="text-xs px-2 py-1 rounded-full bg-accent/15 text-accent-dark whitespace-nowrap"
          >
            Important
          </span>
        </div>

        <p class="text-sm text-muted mb-3">
          Du {{ formaterDate(annonce.date_debut) }} au {{ formaterDate(annonce.date_fin) }}
        </p>

        <p class="whitespace-pre-line leading-relaxed">{{ annonce.contenu }}</p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Annonce {
  id: number
  titre: string
  contenu: string
  type_annonce?: string | null
  date_debut: string
  date_fin: string
  important: boolean
  paroisse_id: number
}

const { request } = useApi()

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
  })
}

const { data: annonces, pending, error } = await useAsyncData(
  'annonces-liste',
  () => request<Annonce[]>(`/annonces?actives_seulement=true&publie=true&limit=50`)
)

const annoncesTriees = computed(() => {
  const liste = annonces.value ?? []
  return [...liste].sort((a, b) => Number(b.important) - Number(a.important))
})
</script>