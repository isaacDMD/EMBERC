<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label mb-2">Administration</p>
        <h1 class="font-display text-3xl font-semibold">Lectures bibliques</h1>
      </div>
      <NuxtLink
        to="/admin/lectures/nouveau"
        class="bg-primary text-white rounded px-4 py-2 text-sm font-medium hover:bg-primary-dark transition"
      >
        + Nouvelle lecture
      </NuxtLink>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Impossible de charger les lectures.</div>
    <div v-else-if="!lectures?.length" class="text-muted text-sm">Aucune lecture pour l'instant.</div>

    <div v-else class="flex flex-col gap-2">
      <NuxtLink
        v-for="lecture in lectures"
        :key="lecture.id"
        :to="`/admin/lectures/${lecture.id}`"
        class="flex items-center justify-between bg-surface border border-ink/10 rounded-lg px-4 py-3 hover:border-primary/40 transition"
      >
        <div>
          <span class="text-xs text-muted">{{ formaterDate(lecture.date_lecture) }}</span>
          <p class="font-medium">{{ lecture.reference }}</p>
        </div>
        <span class="text-sm text-primary">Gérer les lecteurs →</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse', 'resp_lecteurs'],
})

interface Lecture {
  id: number
  reference: string
  date_lecture: string
}

const { request } = useApi()
const auth = useAuthStore()

function formaterDate(iso: string) {
  return new Date(iso).toLocaleString('fr-FR', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  })
}

const { data: lectures, pending, error } = await useAsyncData(
  'admin-lectures-liste',
  () => {
    const filtreParoisse = auth.role !== 'super_admin' && auth.user?.paroisse_id
      ? `&paroisse_id=${auth.user.paroisse_id}`
      : ''
    return request<Lecture[]>(`/lectures?limit=100${filtreParoisse}`)
  }
)
</script>