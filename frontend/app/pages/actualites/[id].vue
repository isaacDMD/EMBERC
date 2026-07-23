<template>
  <div>
    <NuxtLink to="/actualites" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux actualités
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>

    <div v-else-if="error" class="text-sm text-red-600">Cette actualité est introuvable.</div>

    <article v-else-if="actualite">
      <p class="section-label mb-2">{{ formaterDate(actualite.created_at) }}</p>
      <h1 class="font-display text-3xl font-semibold mb-6">{{ actualite.titre }}</h1>
      <BoutonFavori type="article" :item-id="actualite.id" avec-label />

      <img
        v-if="actualite.image_url"
        :src="actualite.image_url"
        :alt="actualite.titre"
        class="w-full rounded-lg mb-6 max-h-96 object-cover"
      />

      <p class="whitespace-pre-line leading-relaxed">{{ actualite.contenu }}</p>
    </article>
  </div>
</template>

<script setup lang="ts">
interface Actualite {
  id: number
  titre: string
  contenu: string
  image_url?: string | null
  created_at: string
}

const route = useRoute()
const { request } = useApi()

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
}

const { data: actualite, pending, error } = await useAsyncData(
  `actualite-${route.params.id}`,
  () => request<Actualite>(`/actualites/${route.params.id}`)
)
</script>