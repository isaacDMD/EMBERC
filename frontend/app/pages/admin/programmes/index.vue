<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label mb-2">Administration</p>
        <h1 class="font-display text-3xl font-semibold">Programmes</h1>
      </div>
      <NuxtLink
        to="/admin/programmes/nouveau"
        class="bg-primary text-white rounded px-4 py-2 text-sm font-medium hover:bg-primary-dark transition"
      >
        + Nouveau programme
      </NuxtLink>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Impossible de charger les programmes.</div>
    <div v-else-if="!programmes?.length" class="text-muted text-sm">Aucun programme pour l'instant.</div>

    <div v-else class="flex flex-col gap-2">
      <NuxtLink
        v-for="programme in programmes"
        :key="programme.id"
        :to="`/admin/programmes/${programme.id}`"
        class="flex items-center justify-between bg-surface border border-ink/10 rounded-lg px-4 py-3 hover:border-primary/40 transition"
      >
        <div>
          <span class="text-xs text-muted">{{ formaterDateHeure(programme.date_heure) }}</span>
          <p class="font-medium">{{ programme.titre }}</p>
        </div>
        <span
          class="text-xs px-2 py-1 rounded-full"
          :class="programme.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted'"
        >
          {{ programme.publie ? 'Publié' : 'Brouillon' }}
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

interface ProgrammeCulte {
  id: number
  titre: string
  date_heure: string
  publie: boolean
}

const { request } = useApi()
const auth = useAuthStore()

function formaterDateHeure(iso: string) {
  return new Date(iso).toLocaleString('fr-FR', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

const { data: programmes, pending, error } = await useAsyncData(
  'admin-programmes-liste',
  () => {
    const filtreParoisse = auth.role !== 'super_admin' && auth.user?.paroisse_id
      ? `&paroisse_id=${auth.user.paroisse_id}`
      : ''
    return request<ProgrammeCulte[]>(`/programmes?limit=100${filtreParoisse}`)
  }
)
</script>