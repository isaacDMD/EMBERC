<template>
  <div class="min-h-screen bg-bg text-ink flex flex-col">
    <header class="border-b border-ink/10 bg-surface">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
        <NuxtLink to="/" class="font-display text-lg font-semibold text-primary">
          EMBERC
        </NuxtLink>

        <button
          class="sm:hidden text-ink"
          aria-label="Ouvrir le menu"
          @click="menuOuvert = !menuOuvert"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <nav class="hidden sm:flex items-center gap-6 text-sm">
          <NuxtLink to="/programmes" class="hover:text-primary">Programmes</NuxtLink>
          <NuxtLink to="/chants" class="hover:text-primary">Chants</NuxtLink>
          <NuxtLink to="/annonces" class="hover:text-primary">Annonces</NuxtLink>
          <template v-if="auth.estConnecte">
            <span class="text-muted">{{ auth.user?.prenom }}</span>
            <button class="text-primary font-medium" @click="auth.logout()">Déconnexion</button>
          </template>
          <NuxtLink v-else to="/connexion" class="text-primary font-medium">Connexion</NuxtLink>
        </nav>
      </div>

      <nav v-if="menuOuvert" class="sm:hidden border-t border-ink/10 px-4 py-3 flex flex-col gap-3 text-sm">
        <NuxtLink to="/programmes" @click="menuOuvert = false">Programmes</NuxtLink>
        <NuxtLink to="/chants" @click="menuOuvert = false">Chants</NuxtLink>
        <NuxtLink to="/annonces" @click="menuOuvert = false">Annonces</NuxtLink>
        <template v-if="auth.estConnecte">
          <span class="text-muted">{{ auth.user?.prenom }}</span>
          <button class="text-left text-primary font-medium" @click="auth.logout()">Déconnexion</button>
        </template>
        <NuxtLink v-else to="/connexion" class="text-primary font-medium">Connexion</NuxtLink>
      </nav>
    </header>

    <main class="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore()
const menuOuvert = ref(false)
</script>