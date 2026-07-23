<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/lectures" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux lectures
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Cette lecture est introuvable.</div>

    <template v-else-if="lecture">
      <p class="section-label mb-2">Administration</p>
      <h1 class="font-display text-2xl font-semibold mb-6">{{ lecture.reference }}</h1>

      <form class="space-y-5 mb-10" @submit.prevent="soumettre">
        <div>
          <label class="block text-sm font-medium mb-1">Référence</label>
          <input
            v-model="reference"
            type="text"
            required
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Date de lecture</label>
          <input
            v-model="dateLecture"
            type="datetime-local"
            required
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Texte (optionnel)</label>
          <textarea
            v-model="texte"
            rows="6"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>
        <p v-if="succes" class="text-sm text-green-700">Lecture mise à jour.</p>

        <button
          type="submit"
          :disabled="chargement"
          class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
        >
          {{ chargement ? 'Enregistrement...' : 'Enregistrer les modifications' }}
        </button>
      </form>

      <div class="divider mb-6" />

      <h2 class="section-label mb-3">Lecteurs assignés</h2>

      <div v-if="lecteursPending" class="text-muted text-sm mb-4">Chargement...</div>
      <ul v-else class="flex flex-col gap-2 mb-6">
        <li
          v-for="l in lecteurs"
          :key="l.id"
          class="flex items-center gap-3 bg-surface border border-ink/10 rounded-lg px-4 py-2"
        >
          <span class="font-medium flex-1">{{ l.prenom }} {{ l.nom }}</span>
          <span class="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary uppercase">{{ l.langue }}</span>
          <button class="text-sm text-red-600 hover:underline" @click="retirerLecteur(l.id)">
            Retirer
          </button>
        </li>
        <li v-if="!lecteurs?.length" class="text-muted text-sm">Aucun lecteur assigné.</li>
      </ul>

      <form class="flex flex-col sm:flex-row gap-2" @submit.prevent="assignerLecteur">
        <select
          v-model="lecteurASelectionner"
          class="flex-1 rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        >
          <option value="" disabled>Choisir un fidèle</option>
          <option v-for="u in utilisateurs" :key="u.id" :value="u.id">
            {{ u.prenom }} {{ u.nom }} ({{ u.identifiant }})
          </option>
        </select>
        <select
          v-model="langueASelectionner"
          class="rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        >
          <option value="fr">Français</option>
          <option value="ewe">Éwé</option>
          <option value="en">Anglais</option>
          <option value="kab">Kabyè</option>
        </select>
        <button
          type="submit"
          class="bg-primary/10 text-primary rounded px-4 py-2 text-sm font-medium hover:bg-primary/20 transition whitespace-nowrap"
        >
          Assigner
        </button>
      </form>
      <p v-if="erreurLecteur" class="text-sm text-red-600 mt-2">{{ erreurLecteur }}</p>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse', 'resp_lecteurs'],
})

interface Lecture {
  id: number
  reference: string
  texte?: string | null
  date_lecture: string
  programme_id: number
  paroisse_id: number
}

interface LecteurAssigne {
  id: number
  lecteur_id: number
  langue: string
  nom: string
  prenom: string
}

interface UtilisateurSimple {
  id: number
  nom: string
  prenom: string
  identifiant: string
  paroisse_id?: number | null
}

const route = useRoute()
const { request } = useApi()

const { data: lecture, pending, error, refresh } = await useAsyncData(
  `admin-lecture-${route.params.id}`,
  () => request<Lecture>(`/lectures/${route.params.id}`)
)

const reference = ref('')
const dateLecture = ref('')
const texte = ref('')
const erreur = ref('')
const succes = ref(false)
const chargement = ref(false)

function isoVersDatetimeLocal(iso: string) {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

watchEffect(() => {
  if (lecture.value) {
    reference.value = lecture.value.reference
    dateLecture.value = isoVersDatetimeLocal(lecture.value.date_lecture)
    texte.value = lecture.value.texte ?? ''
  }
})

async function soumettre() {
  erreur.value = ''
  succes.value = false
  chargement.value = true
  try {
    await request(`/lectures/${route.params.id}`, {
      method: 'PUT',
      body: {
        reference: reference.value,
        texte: texte.value || undefined,
        date_lecture: new Date(dateLecture.value).toISOString(),
      },
    })
    succes.value = true
    await refresh()
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}

const { data: lecteurs, pending: lecteursPending, refresh: refreshLecteurs } = await useAsyncData(
  `admin-lecture-${route.params.id}-lecteurs`,
  () => request<LecteurAssigne[]>(`/lectures/${route.params.id}/lecteurs`)
)

const { data: utilisateurs } = await useAsyncData(
  `admin-lecture-${route.params.id}-utilisateurs`,
  () => request<UtilisateurSimple[]>('/users?limit=200')
)

const lecteurASelectionner = ref<number | ''>('')
const langueASelectionner = ref('fr')
const erreurLecteur = ref('')

async function assignerLecteur() {
  erreurLecteur.value = ''
  if (!lecteurASelectionner.value) return
  try {
    await request(`/lectures/${route.params.id}/lecteurs`, {
      method: 'POST',
      body: { lecteur_id: lecteurASelectionner.value, langue: langueASelectionner.value },
    })
    lecteurASelectionner.value = ''
    langueASelectionner.value = 'fr'
    await refreshLecteurs()
  } catch (e: any) {
    erreurLecteur.value = e?.data?.detail || "Impossible d'assigner ce lecteur."
  }
}

async function retirerLecteur(assocId: number) {
  await request(`/lectures/${route.params.id}/lecteurs/${assocId}`, { method: 'DELETE' })
  await refreshLecteurs()
}
</script>