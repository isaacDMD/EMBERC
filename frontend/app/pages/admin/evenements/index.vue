<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label mb-2">Administration</p>
        <h1 class="font-display text-3xl font-semibold">Événements</h1>
      </div>
      <NuxtLink
        to="/admin/evenements/nouveau"
        class="bg-primary text-white rounded px-4 py-2 text-sm font-medium hover:bg-primary-dark transition"
      >
        + Nouvel événement
      </NuxtLink>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Impossible de charger les événements.</div>
    <div v-else-if="!evenements?.length" class="text-muted text-sm">Aucun événement pour l'instant.</div>

    <div v-else class="flex flex-col gap-2">
      <NuxtLink
        v-for="evenement in evenements"
        :key="evenement.id"
        :to="`/admin/evenements/${evenement.id}`"
        class="flex items-center justify-between bg-surface border border-ink/10 rounded-lg px-4 py-3 hover:border-primary/40 transition"
      >
        <div>
          <span class="text-xs text-muted">
            {{ formaterDate(evenement.date_debut) }} → {{ formaterDate(evenement.date_fin) }}
          </span>
          <p class="font-medium">{{ evenement.titre }}</p>
        </div>
        <span
          class="text-xs px-2 py-1 rounded-full"
          :class="evenement.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted'"
        >
          {{ evenement.publie ? 'Publié' : 'Brouillon' }}
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

interface Evenement {
  id: number
  titre: string
  date_debut: string
  date_fin: string
  publie: boolean
}

const { request } = useApi()
const auth = useAuthStore()

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

const { data: evenements, pending, error } = await useAsyncData(
  'admin-evenements-liste',
  () => {
    const filtreParoisse = auth.role !== 'super_admin' && auth.user?.paroisse_id
      ? `&paroisse_id=${auth.user.paroisse_id}`
      : ''
    return request<Evenement[]>(`/evenements?limit=100${filtreParoisse}`)
  }
)
</script>