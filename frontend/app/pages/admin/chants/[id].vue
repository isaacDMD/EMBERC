<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/chants" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux chants
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Ce chant est introuvable.</div>

    <template v-else-if="chant">
      <p class="section-label mb-2">Administration</p>
      <h1 class="font-display text-3xl font-semibold mb-6">Modifier le chant</h1>

      <form class="space-y-5" @submit.prevent="soumettre">
        <div>
          <label class="block text-sm font-medium mb-1">Numéro</label>
          <input
            v-model="numero"
            type="text"
            required
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

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
          <label class="block text-sm font-medium mb-1">Catégorie</label>
          <select
            v-model="categorie"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          >
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Auteur (optionnel)</label>
          <input
            v-model="auteur"
            type="text"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Paroles (optionnel)</label>
          <textarea
            v-model="paroles"
            rows="6"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Fichier audio</label>
          <audio v-if="chant.fichier_audio_url && !fichierAudio" :src="chant.fichier_audio_url" controls class="w-full mb-2" />
          <input
            type="file"
            accept="audio/mpeg,audio/mp3,audio/wav,audio/ogg"
            class="w-full text-sm"
            @change="onFichierChange"
          />
          <p v-if="fichierAudio" class="text-xs text-muted mt-1">
            Nouveau fichier sélectionné : {{ fichierAudio.name }}
          </p>
        </div>

        <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>
        <p v-if="succes" class="text-sm text-green-700">Chant mis à jour avec succès.</p>

        <button
          type="submit"
          :disabled="chargement"
          class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
        >
          {{ chargement ? statutChargement : 'Enregistrer les modifications' }}
        </button>
      </form>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse', 'resp_musical'],
})

interface Chant {
  id: number
  numero: string
  titre: string
  categorie: string
  auteur?: string | null
  paroles?: string | null
  fichier_audio_url?: string | null
}

const categories = [
  { value: 'chant', label: 'Chant' },
  { value: 'chant_de_messe', label: 'Chant de messe' },
  { value: 'chant_de_la_saintete', label: 'Sainteté' },
  { value: 'chant_de_la_vie', label: 'Vie' },
  { value: 'chant_de_la_paix', label: 'Paix' },
  { value: 'chant_de_la_joie', label: 'Joie' },
]

const route = useRoute()
const { request } = useApi()
const { uploaderAudio } = useChantAudioUpload()

const { data: chant, pending, error } = await useAsyncData(
  `admin-chant-${route.params.id}`,
  () => request<Chant>(`/chants/${route.params.id}`)
)

const numero = ref('')
const titre = ref('')
const categorie = ref('chant')
const auteur = ref('')
const paroles = ref('')
const fichierAudio = ref<File | null>(null)
const erreur = ref('')
const succes = ref(false)
const chargement = ref(false)
const statutChargement = ref('Enregistrement...')

watchEffect(() => {
  if (chant.value) {
    numero.value = chant.value.numero
    titre.value = chant.value.titre
    categorie.value = chant.value.categorie
    auteur.value = chant.value.auteur ?? ''
    paroles.value = chant.value.paroles ?? ''
  }
})

function onFichierChange(event: Event) {
  const input = event.target as HTMLInputElement
  fichierAudio.value = input.files?.[0] ?? null
}

async function soumettre() {
  erreur.value = ''
  succes.value = false
  chargement.value = true
  try {
    let fichier_audio_url: string | undefined

    if (fichierAudio.value) {
      statutChargement.value = "Envoi du fichier audio..."
      fichier_audio_url = await uploaderAudio(fichierAudio.value)
    }

    statutChargement.value = "Enregistrement..."
    await request(`/chants/${route.params.id}`, {
      method: 'PUT',
      body: {
        numero: numero.value,
        titre: titre.value,
        categorie: categorie.value,
        auteur: auteur.value || undefined,
        paroles: paroles.value || undefined,
        ...(fichier_audio_url ? { fichier_audio_url } : {}),
      },
    })
    succes.value = true
    fichierAudio.value = null
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}
</script>