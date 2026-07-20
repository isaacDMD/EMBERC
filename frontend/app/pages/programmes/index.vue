<template>
  <div>
    <p class="section-label mb-2">Vie de l'église</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Programmes des cultes</h1>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement des programmes...</div>

    <div v-else-if="error" class="text-sm text-red-600">
      Impossible de charger les programmes pour le moment.
    </div>

    <div v-else-if="!programmes?.length" class="text-muted text-sm">
      Aucun programme n'est prévu pour l'instant.
    </div>

    <div v-else class="flex flex-col gap-4">
      <NuxtLink
        v-for="programme in programmes"
        :key="programme.id"
        :to="`/programmes/${programme.id}`"
        class="bg-surface border border-ink/10 rounded-lg p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 hover:border-primary/40 transition"
      >
        <div>
          <p class="section-label mb-1">{{ formaterDateHeure(programme.date_heure) }}</p>
          <h2 class="font-display text-lg font-semibold">{{ programme.titre }}</h2>
          <p v-if="programme.predicateur" class="text-sm text-muted mt-1">
            {{ programme.predicateur }}
          </p>
        </div>
        <span class="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary whitespace-nowrap self-start sm:self-center">
          {{ programme.type_culte }}
        </span>
      </NuxtLink>
    </div>

    <div class="flex items-center justify-between mt-8" v-if="!pending && programmes?.length">
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
        :disabled="programmes.length < limit"
        @click="page++"
      >
        Suivant →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ProgrammeCulte {
  id: number
  titre: string
  type_culte: string
  predicateur?: string | null
  date_heure: string
  paroisse_id: number
  publie: boolean
}

const { request } = useApi()
const page = ref(1)
const limit = 12

function formaterDateHeure(iso: string) {
  const date = new Date(iso)
  return date.toLocaleString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const { data: programmes, pending, error } = await useAsyncData(
  'programmes-liste',
  () => request<ProgrammeCulte[]>(`/programmes?page=${page.value}&limit=${limit}&publie=true`),
  { watch: [page] }
)
</script>