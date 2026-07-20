<template>
  <div>
    <!-- Hero -->
    <section class="mb-12">
      <p class="section-label mb-2">EMBERC</p>
      <h1 class="font-display text-4xl sm:text-5xl font-semibold leading-tight mb-3">
        Bienvenue{{ auth.user ? `, ${auth.user.prenom}` : '' }}
      </h1>
      <p class="text-muted text-lg max-w-xl">
        Programmes, chants, lectures et annonces de l'Église Mission Baptiste
        Évangélique Royaume du Christ, réunis en un seul endroit.
      </p>
    </section>

    <!-- Prochain culte -->
    <section class="mb-12">
      <p class="section-label mb-3">Prochain culte</p>
      <div class="divider mb-5" />

      <div v-if="programmePending" class="text-muted text-sm">Chargement...</div>
      <div v-else-if="!prochainProgramme" class="text-muted text-sm">
        Aucun programme à venir n'est publié pour l'instant.
      </div>
      <NuxtLink
        v-else
        :to="`/programmes/${prochainProgramme.id}`"
        class="block bg-surface border border-ink/10 rounded-lg p-6 hover:border-primary/40 transition"
      >
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <p class="section-label mb-1">{{ formaterDateHeure(prochainProgramme.date_heure) }}</p>
            <h2 class="font-display text-2xl font-semibold">{{ prochainProgramme.titre }}</h2>
            <p v-if="prochainProgramme.predicateur" class="text-sm text-muted mt-1">
              {{ prochainProgramme.predicateur }}
            </p>
          </div>
          <span class="text-xs px-3 py-1.5 rounded-full bg-primary/10 text-primary whitespace-nowrap self-start">
            {{ prochainProgramme.type_culte }}
          </span>
        </div>
      </NuxtLink>
    </section>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
      <!-- Annonces importantes -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <p class="section-label">Annonces</p>
          <NuxtLink to="/annonces" class="text-sm text-primary hover:underline">Tout voir →</NuxtLink>
        </div>
        <div class="divider mb-5" />

        <div v-if="annoncesPending" class="text-muted text-sm">Chargement...</div>
        <p v-else-if="!annonces?.length" class="text-muted text-sm">
          Aucune annonce active pour le moment.
        </p>
        <div v-else class="flex flex-col gap-3">
          <div
            v-for="annonce in annonces.slice(0, 3)"
            :key="annonce.id"
            class="bg-surface border rounded-lg p-4"
            :class="annonce.important ? 'border-accent/50 ring-1 ring-accent/20' : 'border-ink/10'"
          >
            <h3 class="font-medium mb-1">{{ annonce.titre }}</h3>
            <p class="text-sm text-muted line-clamp-2">{{ annonce.contenu }}</p>
          </div>
        </div>
      </section>

      <!-- Dernières actualités -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <p class="section-label">Actualités</p>
          <NuxtLink to="/actualites" class="text-sm text-primary hover:underline">Tout voir →</NuxtLink>
        </div>
        <div class="divider mb-5" />

        <div v-if="actualitesPending" class="text-muted text-sm">Chargement...</div>
        <p v-else-if="!actualites?.length" class="text-muted text-sm">
          Aucune actualité publiée pour le moment.
        </p>
        <div v-else class="flex flex-col gap-3">
          <NuxtLink
            v-for="actu in actualites.slice(0, 3)"
            :key="actu.id"
            :to="`/actualites/${actu.id}`"
            class="bg-surface border border-ink/10 rounded-lg p-4 hover:border-primary/40 transition"
          >
            <h3 class="font-medium mb-1">{{ actu.titre }}</h3>
            <p v-if="actu.resume" class="text-sm text-muted line-clamp-2">{{ actu.resume }}</p>
          </NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

interface ProgrammeCulte {
  id: number
  titre: string
  type_culte: string
  predicateur?: string | null
  date_heure: string
}

interface Annonce {
  id: number
  titre: string
  contenu: string
  important: boolean
}

interface Actualite {
  id: number
  titre: string
  resume?: string | null
}

const auth = useAuthStore()
const { request } = useApi()

function formaterDateHeure(iso: string) {
  return new Date(iso).toLocaleString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const { data: programmes, pending: programmePending } = await useAsyncData(
  'accueil-programmes',
  () => request<ProgrammeCulte[]>('/programmes?publie=true&limit=20')
)
const prochainProgramme = computed(() => {
  const maintenant = new Date()
  return (programmes.value ?? [])
    .filter((p) => new Date(p.date_heure) >= maintenant)
    .sort((a, b) => new Date(a.date_heure).getTime() - new Date(b.date_heure).getTime())[0] ?? null
})

const { data: annonces, pending: annoncesPending } = await useAsyncData(
  'accueil-annonces',
  () => request<Annonce[]>('/annonces?actives_seulement=true&publie=true&limit=5')
)

const { data: actualites, pending: actualitesPending } = await useAsyncData(
  'accueil-actualites',
  () => request<Actualite[]>('/actualites?publie=true&limit=5')
)
</script>