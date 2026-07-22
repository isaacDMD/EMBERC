<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label mb-2">Administration</p>
        <h1 class="font-display text-3xl font-semibold">Actualités</h1>
      </div>
      <NuxtLink
        to="/admin/actualites/nouveau"
        class="bg-primary text-white rounded px-4 py-2 text-sm font-medium hover:bg-primary-dark transition"
      >
        + Nouvelle actualité
      </NuxtLink>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Impossible de charger les actualités.</div>
    <div v-else-if="!actualites?.length" class="text-muted text-sm">Aucune actualité pour l'instant.</div>

    <div v-else class="flex flex-col gap-2">
      <NuxtLink
        v-for="actu in actualites"
        :key="actu.id"
        :to="`/admin/actualites/${actu.id}`"
        class="flex items-center justify-between bg-surface border border-ink/10 rounded-lg px-4 py-3 hover:border-primary/40 transition"
      >
        <p class="font-medium">{{ actu.titre }}</p>
        <span
          class="text-xs px-2 py-1 rounded-full"
          :class="actu.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted'"
        >
          {{ actu.publie ? 'Publié' : 'Brouillon' }}
        </span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse'],
})

interface Actualite {
  id: number
  titre: string
  publie: boolean
}

const { request } = useApi()
const auth = useAuthStore()

const { data: actualites, pending, error } = await useAsyncData(
  'admin-actualites-liste',
  () => {
    const filtreParoisse = auth.role !== 'super_admin' && auth.user?.paroisse_id
      ? `&paroisse_id=${auth.user.paroisse_id}`
      : ''
    return request<Actualite[]>(`/actualites?limit=100${filtreParoisse}`)
  }
)
</script>