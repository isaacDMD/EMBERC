<template>
  <div>
    <p class="section-label mb-2">Vie de l'église</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Événements à venir</h1>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement des événements...</div>

    <div v-else-if="error" class="text-sm text-red-600">
      Impossible de charger les événements pour le moment.
    </div>

    <div v-else-if="!evenements?.length" class="text-muted text-sm">
      Aucun événement à venir pour le moment.
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <article
        v-for="evenement in evenements"
        :key="evenement.id"
        class="bg-surface border border-ink/10 rounded-lg overflow-hidden flex flex-col"
      >
        <img
          v-if="evenement.image_url"
          :src="evenement.image_url"
          :alt="evenement.titre"
          class="w-full h-40 object-cover"
        />
        <div class="p-5 flex flex-col gap-2 flex-1">
          <p class="section-label">
            {{ formaterPeriode(evenement.date_debut, evenement.date_fin) }}
          </p>
          <h2 class="font-display text-lg font-semibold">{{ evenement.titre }}</h2>
          <p v-if="evenement.lieu" class="text-sm text-muted">📍 {{ evenement.lieu }}</p>
          <p v-if="evenement.description" class="text-sm leading-relaxed mt-1">
            {{ evenement.description }}
          </p>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Evenement {
  id: number
  titre: string
  description?: string | null
  date_debut: string
  date_fin: string
  lieu?: string | null
  image_url?: string | null
  type_evenement?: string | null
}

const { request } = useApi()

function formaterPeriode(debut: string, fin: string) {
  const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'long' }
  const d = new Date(debut).toLocaleDateString('fr-FR', options)
  const f = new Date(fin).toLocaleDateString('fr-FR', options)
  return d === f ? d : `${d} → ${f}`
}

const { data: evenements, pending, error } = await useAsyncData(
  'evenements-liste',
  () => request<Evenement[]>(`/evenements?a_venir_seulement=true&publie=true&limit=50`)
)
</script>