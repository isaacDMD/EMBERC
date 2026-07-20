<template>
  <div>
    <p class="section-label mb-2">Administration</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Espace de gestion</h1>

    <div class="divider mb-6" />

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <NuxtLink
        v-for="section in sectionsVisibles"
        :key="section.href"
        :to="section.href"
        class="bg-surface border border-ink/10 rounded-lg p-5 hover:border-primary/40 transition"
      >
        <h2 class="font-display text-lg font-semibold mb-1">{{ section.titre }}</h2>
        <p class="text-sm text-muted">{{ section.description }}</p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth';

definePageMeta({ middleware: 'admin' })

const auth = useAuthStore()

const sections = [
  {
    titre: 'Chants',
    description: 'Ajouter, modifier et gérer les fichiers audio des chants.',
    href: '/admin/chants',
    roles: ['super_admin', 'admin_paroisse', 'resp_musical'],
  },
  {
    titre: 'Programmes',
    description: 'Créer et publier les programmes de culte.',
    href: '/admin/programmes',
    roles: ['super_admin', 'admin_paroisse'],
  },
  {
    titre: 'Annonces',
    description: 'Publier des annonces pour votre paroisse.',
    href: '/admin/annonces',
    roles: ['super_admin', 'admin_paroisse'],
  },
  {
    titre: 'Événements',
    description: 'Créer et gérer les événements à venir.',
    href: '/admin/evenements',
    roles: ['super_admin', 'admin_paroisse'],
  },
  {
    titre: 'Médias',
    description: 'Ajouter des photos, vidéos, audios et documents.',
    href: '/admin/medias',
    roles: ['super_admin', 'admin_paroisse'],
  },
  {
    titre: 'Actualités',
    description: 'Rédiger et publier des articles.',
    href: '/admin/actualites',
    roles: ['super_admin', 'admin_paroisse'],
  },
]

const sectionsVisibles = computed(() =>
  sections.filter((s) => s.roles.includes(auth.role ?? ''))
)
</script>