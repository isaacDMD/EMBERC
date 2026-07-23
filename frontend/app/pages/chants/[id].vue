<template>
  <div>
    <NuxtLink to="/chants" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux chants
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>

    <div v-else-if="error" class="text-sm text-red-600">Ce chant est introuvable.</div>

    <div v-else-if="chant">
      <p class="section-label mb-2">N° {{ chant.numero }}</p>
      <h1 class="font-display text-3xl font-semibold mb-2">{{ chant.titre }}</h1>
      <p v-if="chant.auteur" class="text-muted mb-6">{{ chant.auteur }}</p>
      <p>TEST BOUTON : {{ auth.estConnecte }}</p>
      <BoutonFavori type="chant" :item-id="chant.id" avec-label />

      <audio
        v-if="chant.fichier_audio_url"
        :src="chant.fichier_audio_url"
        controls
        class="w-full mb-6"
      />

      <div class="divider mb-6" />

      <p v-if="chant.paroles" class="whitespace-pre-line leading-relaxed">{{ chant.paroles }}</p>
      <p v-else class="text-muted text-sm">Les paroles de ce chant n'ont pas encore été ajoutées.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

interface Chant {
  id: number
  numero: string
  titre: string
  paroles?: string | null
  categorie: string
  auteur?: string | null
  fichier_audio_url?: string | null
}

const route = useRoute()
const { request } = useApi()
const auth = useAuthStore()

const { data: chant, pending, error } = await useAsyncData(
  `chant-${route.params.id}`,
  () => request<Chant>(`/chants/${route.params.id}`)
)
</script>