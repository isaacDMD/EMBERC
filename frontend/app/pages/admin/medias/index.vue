<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label mb-2">Administration</p>
        <h1 class="font-display text-3xl font-semibold">Médias</h1>
      </div>
      <NuxtLink
        to="/admin/medias/nouveau"
        class="bg-primary text-white rounded px-4 py-2 text-sm font-medium hover:bg-primary-dark transition"
      >
        + Nouveau média
      </NuxtLink>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Impossible de charger les médias.</div>
    <div v-else-if="!medias?.length" class="text-muted text-sm">Aucun média pour l'instant.</div>

    <div v-else class="flex flex-col gap-2">
      <NuxtLink
        v-for="media in medias"
        :key="media.id"
        :to="`/admin/medias/${media.id}`"
        class="flex items-center justify-between bg-surface border border-ink/10 rounded-lg px-4 py-3 hover:border-primary/40 transition"
      >
        <div>
          <span class="text-xs text-muted uppercase">{{ media.type_media }}</span>
          <p class="font-medium">{{ media.titre }}</p>
        </div>
        <span
          class="text-xs px-2 py-1 rounded-full"
          :class="media.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted'"
        >
          {{ media.publie ? 'Publié' : 'Brouillon' }}
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

interface Media {
  id: number
  titre: string
  type_media: string
  publie: boolean
}

const { request } = useApi()
const auth = useAuthStore()

const { data: medias, pending, error } = await useAsyncData(
  'admin-medias-liste',
  () => {
    const filtreParoisse = auth.role !== 'super_admin' && auth.user?.paroisse_id
      ? `&paroisse_id=${auth.user.paroisse_id}`
      : ''
    return request<Media[]>(`/medias?limit=100${filtreParoisse}`)
  }
)
</script>