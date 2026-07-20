<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/evenements" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux événements
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Cet événement est introuvable.</div>

    <template v-else-if="evenement">
      <div class="flex items-center justify-between mb-6">
        <div>
          <p class="section-label mb-2">Administration</p>
          <h1 class="font-display text-2xl font-semibold">{{ evenement.titre }}</h1>
        </div>
        <button
          class="text-xs px-3 py-1.5 rounded-full transition whitespace-nowrap"
          :class="evenement.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted hover:bg-ink/10'"
          @click="basculerPublication"
        >
          {{ evenement.publie ? 'Publié — dépublier' : 'Brouillon — publier' }}
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

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium mb-1">Date de début</label>
            <input
              v-model="dateDebut"
              type="date"
              required
              class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Date de fin</label>
            <input
              v-model="dateFin"
              type="date"
              required
              class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Lieu (optionnel)</label>
          <input
            v-model="lieu"
            type="text"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Description (optionnel)</label>
          <textarea
            v-model="description"
            rows="4"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
        <label class="block text-sm font-medium mb-1">Affiche</label>
        <img
            v-if="evenement.image_url && !fichierAffiche"
            :src="evenement.image_url"
            alt="Affiche actuelle"
            class="w-full max-h-48 object-cover rounded mb-2"
        />
        <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="w-full text-sm"
            @change="onFichierChange"
        />
        <p v-if="fichierAffiche" class="text-xs text-muted mt-1">
            Nouvelle affiche sélectionnée : {{ fichierAffiche.name }}
        </p>
        </div>

        <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>
        <p v-if="succes" class="text-sm text-green-700">Événement mis à jour.</p>

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
        Supprimer cet événement
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse'],
})

interface Evenement {
  id: number
  titre: string
  description?: string | null
  date_debut: string
  date_fin: string
  lieu?: string | null
  image_url?: string | null
  publie: boolean
  paroisse_id: number
}

const route = useRoute()
const { request } = useApi()

const { data: evenement, pending, error, refresh } = await useAsyncData(
  `admin-evenement-${route.params.id}`,
  () => request<Evenement>(`/evenements/${route.params.id}`)
)

const titre = ref('')
const dateDebut = ref('')
const dateFin = ref('')
const lieu = ref('')
const description = ref('')
const imageUrl = ref('')
const erreur = ref('')
const succes = ref(false)
const chargement = ref(false)

watchEffect(() => {
  if (evenement.value) {
    titre.value = evenement.value.titre
    dateDebut.value = evenement.value.date_debut
    dateFin.value = evenement.value.date_fin
    lieu.value = evenement.value.lieu ?? ''
    description.value = evenement.value.description ?? ''
    imageUrl.value = evenement.value.image_url ?? ''
  }
})

const { uploaderFichier } = useMediaUpload()
const fichierAffiche = ref<File | null>(null)
const statutChargement = ref('Enregistrement...')

function onFichierChange(event: Event) {
  const input = event.target as HTMLInputElement
  fichierAffiche.value = input.files?.[0] ?? null
}

async function soumettre() {
  erreur.value = ''
  succes.value = false
  chargement.value = true
  try {
    let image_url: string | undefined

    if (fichierAffiche.value && evenement.value) {
      statutChargement.value = "Envoi de l'affiche..."
      image_url = await uploaderFichier(fichierAffiche.value, 'image', evenement.value.paroisse_id)
    }

    statutChargement.value = "Enregistrement..."
    await request(`/evenements/${route.params.id}`, {
      method: 'PUT',
      body: {
        titre: titre.value,
        date_debut: dateDebut.value,
        date_fin: dateFin.value,
        lieu: lieu.value || undefined,
        description: description.value || undefined,
        ...(image_url ? { image_url } : {}),
      },
    })
    succes.value = true
    fichierAffiche.value = null
    await refresh()
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}

async function basculerPublication() {
  if (!evenement.value) return
  await request(`/evenements/${route.params.id}`, {
    method: 'PUT',
    body: { publie: !evenement.value.publie },
  })
  await refresh()
}

async function supprimer() {
  if (!confirm('Supprimer définitivement cet événement ?')) return
  await request(`/evenements/${route.params.id}`, { method: 'DELETE' })
  await navigateTo('/admin/evenements')
}
</script>