<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/actualites" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux actualités
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Cette actualité est introuvable.</div>

    <template v-else-if="actualite">
      <div class="flex items-center justify-between mb-6">
        <div>
          <p class="section-label mb-2">Administration</p>
          <h1 class="font-display text-2xl font-semibold">{{ actualite.titre }}</h1>
        </div>
        <button
          class="text-xs px-3 py-1.5 rounded-full transition whitespace-nowrap"
          :class="actualite.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted hover:bg-ink/10'"
          @click="basculerPublication"
        >
          {{ actualite.publie ? 'Publié — dépublier' : 'Brouillon — publier' }}
        </button>
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
          <label class="block text-sm font-medium mb-1">Résumé (optionnel)</label>
          <input
            v-model="resume"
            type="text"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Contenu</label>
          <textarea
            v-model="contenu"
            rows="8"
            required
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Image</label>
          <img
            v-if="actualite.image_url && !fichier"
            :src="actualite.image_url"
            class="w-full max-h-48 object-cover rounded mb-2"
          />
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="w-full text-sm"
            @change="onFichierChange"
          />
          <p v-if="fichier" class="text-xs text-muted mt-1">
            Nouvelle image sélectionnée : {{ fichier.name }}
          </p>
        </div>

        <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>
        <p v-if="succes" class="text-sm text-green-700">Actualité mise à jour.</p>

        <button
          type="submit"
          :disabled="chargement"
          class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
        >
          {{ chargement ? statutChargement : 'Enregistrer les modifications' }}
        </button>
      </form>

      <div class="divider my-6" />

      <button class="text-sm text-red-600 hover:underline" @click="supprimer">
        Supprimer cette actualité
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse'],
})

interface Actualite {
  id: number
  titre: string
  resume?: string | null
  contenu: string
  image_url?: string | null
  publie: boolean
  paroisse_id: number
}

const route = useRoute()
const { request } = useApi()
const { uploaderFichier } = useMediaUpload()

const { data: actualite, pending, error, refresh } = await useAsyncData(
  `admin-actualite-${route.params.id}`,
  () => request<Actualite>(`/actualites/${route.params.id}`)
)

const titre = ref('')
const resume = ref('')
const contenu = ref('')
const fichier = ref<File | null>(null)
const erreur = ref('')
const succes = ref(false)
const chargement = ref(false)
const statutChargement = ref('Enregistrement...')

watchEffect(() => {
  if (actualite.value) {
    titre.value = actualite.value.titre
    resume.value = actualite.value.resume ?? ''
    contenu.value = actualite.value.contenu
  }
})

function onFichierChange(event: Event) {
  const input = event.target as HTMLInputElement
  fichier.value = input.files?.[0] ?? null
}

async function soumettre() {
  erreur.value = ''
  succes.value = false
  chargement.value = true
  try {
    let image_url: string | undefined
    if (fichier.value && actualite.value) {
      statutChargement.value = "Envoi de l'image..."
      image_url = await uploaderFichier(fichier.value, 'image', actualite.value.paroisse_id)
    }

    statutChargement.value = "Enregistrement..."
    await request(`/actualites/${route.params.id}`, {
      method: 'PUT',
      body: {
        titre: titre.value,
        resume: resume.value || undefined,
        contenu: contenu.value,
        ...(image_url ? { image_url } : {}),
      },
    })
    succes.value = true
    fichier.value = null
    await refresh()
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}

async function basculerPublication() {
  if (!actualite.value) return
  await request(`/actualites/${route.params.id}`, {
    method: 'PUT',
    body: { publie: !actualite.value.publie },
  })
  await refresh()
}

async function supprimer() {
  if (!confirm('Supprimer définitivement cette actualité ?')) return
  await request(`/actualites/${route.params.id}`, { method: 'DELETE' })
  await navigateTo('/admin/actualites')
}
</script>