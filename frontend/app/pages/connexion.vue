<template>
  <div class="bg-surface border border-ink/10 rounded-lg p-8 shadow-sm">
    <p class="section-label mb-2">Connexion</p>
    <h1 class="font-display text-2xl font-semibold mb-6">Bienvenue sur EMBERC</h1>

    <form class="space-y-4" @submit.prevent="soumettre">
      <div>
        <label for="identifiant" class="block text-sm font-medium mb-1">Identifiant</label>
        <input
          id="identifiant"
          v-model="identifiant"
          type="text"
          required
          autocomplete="username"
          class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        />
      </div>

      <div>
        <label for="mot_de_passe" class="block text-sm font-medium mb-1">Mot de passe</label>
        <input
          id="mot_de_passe"
          v-model="motDePasse"
          type="password"
          required
          autocomplete="current-password"
          class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        />
      </div>

      <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>

      <button
        type="submit"
        :disabled="chargement"
        class="w-full bg-primary text-white rounded py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
      >
        {{ chargement ? 'Connexion...' : 'Se connecter' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { navigateTo } from 'nuxt/app'
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'

definePageMeta({ layout: 'connexion', middleware: 'invite' })

const identifiant = ref('')
const motDePasse = ref('')
const erreur = ref('')
const chargement = ref(false)
const auth = useAuthStore()

async function soumettre() {
  erreur.value = ''
  chargement.value = true
  try {
    await auth.login(identifiant.value, motDePasse.value)
    await navigateTo('/')
  } catch (e: any) {
    erreur.value = 'Identifiant ou mot de passe incorrect'
  } finally {
    chargement.value = false
  }
}
</script>