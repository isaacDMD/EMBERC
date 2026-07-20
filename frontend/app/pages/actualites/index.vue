<template>
  <div>
    <p class="section-label mb-2">Vie de l'église</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Actualités</h1>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement des actualités...</div>

    <div v-else-if="error" class="text-sm text-red-600">
      Impossible de charger les actualités pour le moment.
    </div>

    <div v-else-if="!actualites?.length" class="text-muted text-sm">
      Aucune actualité publiée pour le moment.
    </div>

    <div v-else class="flex flex-col gap-4">
      <NuxtLink
        v-for="actu in actualites"
        :key="actu.id"
        :to="`/actualites/${actu.id}`"
        class="bg-surface border border-ink/10 rounded-lg overflow-hidden flex flex-col sm:flex-row hover:border-primary/40 transition"
      >
        <img
          v-if="actu.image_url"
          :src="actu.image_url"
          :alt="actu.titre"
          class="w-full sm:w-48 h-40 sm:h-auto object-cover"
        />
        <div class="p-5 flex flex-col gap-2">
          <p class="section-label">{{ formaterDate(actu.created_at) }}</p>
          <h2 class="font-display text-lg font-semibold">{{ actu.titre }}</h2>
          <p v-if="actu.resume" class="text-sm text-muted leading-relaxed">{{ actu.resume }}</p>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Actualite {
  id: number
  titre: string
  resume?: string | null
  image_url?: string | null
  created_at: string
}

const { request } = useApi()

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
}

const { data: actualites, pending, error } = await useAsyncData(
  'actualites-liste',
  () => request<Actualite[]>(`/actualites?publie=true&limit=50`)
)
</script>