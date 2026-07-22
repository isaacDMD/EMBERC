<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/medias" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux médias
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Ce média est introuvable.</div>

    <template v-else-if="media">
      <div class="flex items-center justify-between mb-6">
        <div>
          <p class="section-label mb-2">Administration</p>
          <h1 class="font-display text-2xl font-semibold">{{ media.titre }}</h1>
        </div>
        <button
          class="text-xs px-3 py-1.5 rounded-full transition whitespace-nowrap"
          :class="media.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted hover:bg-ink/10'"
          @click="basculerPublication"
        >
          {{ media.publie ? 'Publié — dépublier' : 'Brouillon — publier' }}
        </button>
      </div>

      <div class="mb-6">
        <img v-if="media.type_media === 'image'" :src="media.url_media" class="w-full rounded-lg max-h-64 object-cover" />
        <audio v-else-if="media.type_media === 'audio'" :src="media.url_media" controls class="w-full" />
        <video v-else-if="media.type_media === 'video'" :src="media.url_media" controls class="w-full rounded-lg" />
        <a v-else :href="media.url_media" target="_blank" rel="noopener" class="text-primary hover:underline text-sm">
          Ouvrir le document ↗
        </a>
      </div>

      <form class="space-y-5" @submit.prevent="soumettre">
        <div>
          <label class="block text-sm font-medium mb-1">Titre</label>
          <input
            v-model="titre"
            type="text"
            required
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Description (optionnel)</label>
          <textarea
            v-model="description"
            rows="3"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>
        <p v-if="succes" class="text-sm text-green-700">Média mis à jour.</p>

        <button
          type="submit"
          :disabled="chargement"
          class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
        >
          {{ chargement ? 'Enregistrement...' : 'Enregistrer les modifications' }}
        </button>
      </form>

      <div class="divider my-6" />

      <button class="text-sm text-red-600 hover:underline" @click="supprimer">
        Supprimer ce média
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse'],
})

interface Media {
  id: number
  titre: string
  type_media: string
  description?: string | null
  url_media: string
  publie: boolean
}

const route = useRoute()
const { request } = useApi()

const { data: media, pending, error, refresh } = await useAsyncData(
  `admin-media-${route.params.id}`,
  () => request<Media>(`/medias/${route.params.id}`)
)

const titre = ref('')
const description = ref('')
const erreur = ref('')
const succes = ref(false)
const chargement = ref(false)

watchEffect(() => {
  if (media.value) {
    titre.value = media.value.titre
    description.value = media.value.description ?? ''
  }
})

async function soumettre() {
  erreur.value = ''
  succes.value = false
  chargement.value = true
  try {
    await request(`/medias/${route.params.id}`, {
      method: 'PUT',
      body: { titre: titre.value, description: description.value || undefined },
    })
    succes.value = true
    await refresh()
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}

async function basculerPublication() {
  if (!media.value) return
  await request(`/medias/${route.params.id}`, {
    method: 'PUT',
    body: { publie: !media.value.publie },
  })
  await refresh()
}

async function supprimer() {
  if (!confirm('Supprimer définitivement ce média ?')) return
  await request(`/medias/${route.params.id}`, { method: 'DELETE' })
  await navigateTo('/admin/medias')
}
</script>