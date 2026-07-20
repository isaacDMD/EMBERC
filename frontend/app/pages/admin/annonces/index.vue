<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label mb-2">Administration</p>
        <h1 class="font-display text-3xl font-semibold">Annonces</h1>
      </div>
      <NuxtLink
        to="/admin/annonces/nouveau"
        class="bg-primary text-white rounded px-4 py-2 text-sm font-medium hover:bg-primary-dark transition"
      >
        + Nouvelle annonce
      </NuxtLink>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Impossible de charger les annonces.</div>
    <div v-else-if="!annonces?.length" class="text-muted text-sm">Aucune annonce pour l'instant.</div>

    <div v-else class="flex flex-col gap-2">
      <NuxtLink
        v-for="annonce in annonces"
        :key="annonce.id"
        :to="`/admin/annonces/${annonce.id}`"
        class="flex items-center justify-between bg-surface border border-ink/10 rounded-lg px-4 py-3 hover:border-primary/40 transition"
      >
        <div>
          <span class="text-xs text-muted">
            Du {{ formaterDate(annonce.date_debut) }} au {{ formaterDate(annonce.date_fin) }}
          </span>
          <p class="font-medium">{{ annonce.titre }}</p>
        </div>
        <div class="flex items-center gap-2">
          <span v-if="annonce.important" class="text-xs px-2 py-1 rounded-full bg-accent/15 text-accent-dark">
            Important
          </span>
          <span
            class="text-xs px-2 py-1 rounded-full"
            :class="annonce.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted'"
          >
            {{ annonce.publie ? 'Publié' : 'Brouillon' }}
          </span>
        </div>
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

interface Annonce {
  id: number
  titre: string
  date_debut: string
  date_fin: string
  important: boolean
  publie: boolean
}

const { request } = useApi()
const auth = useAuthStore()

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

const { data: annonces, pending, error } = await useAsyncData(
  'admin-annonces-liste',
  () => {
    const filtreParoisse = auth.role !== 'super_admin' && auth.user?.paroisse_id
      ? `&paroisse_id=${auth.user.paroisse_id}`
      : ''
    return request<Annonce[]>(`/annonces?limit=100${filtreParoisse}`)
  }
)
</script>