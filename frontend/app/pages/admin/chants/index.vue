<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <p class="section-label mb-2">Administration</p>
        <h1 class="font-display text-3xl font-semibold">Chants</h1>
      </div>
      <NuxtLink
        to="/admin/chants/nouveau"
        class="bg-primary text-white rounded px-4 py-2 text-sm font-medium hover:bg-primary-dark transition"
      >
        + Nouveau chant
      </NuxtLink>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Impossible de charger les chants.</div>
    <div v-else-if="!chants?.length" class="text-muted text-sm">Aucun chant pour l'instant.</div>

    <div v-else class="flex flex-col gap-2">
      <NuxtLink
        v-for="chant in chants"
        :key="chant.id"
        :to="`/admin/chants/${chant.id}`"
        class="flex items-center justify-between bg-surface border border-ink/10 rounded-lg px-4 py-3 hover:border-primary/40 transition"
      >
        <div>
          <span class="text-xs text-muted">N° {{ chant.numero }}</span>
          <p class="font-medium">{{ chant.titre }}</p>
        </div>
        <span class="text-sm text-primary">Modifier →</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse', 'resp_musical'],
})

interface Chant {
  id: number
  numero: string
  titre: string
}

const { request } = useApi()

const { data: chants, pending, error } = await useAsyncData(
  'admin-chants-liste',
  () => request<Chant[]>('/chants?limit=100')
)
</script>