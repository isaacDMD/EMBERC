<template>
  <div>
    <p class="section-label mb-2">Accueil</p>
    <h1 class="font-display text-3xl font-semibold mb-6">
      Bienvenue{{ auth.user ? `, ${auth.user.prenom}` : '' }}
    </h1>
    <div class="divider mb-6" />
    <p class="text-muted">
      Le tableau de bord arrivera bientôt : programmes à venir, dernières annonces, chants récents.
    </p>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../stores/auth';

const auth = useAuthStore()
</script>