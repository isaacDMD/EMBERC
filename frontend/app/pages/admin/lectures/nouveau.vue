<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/lectures" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux lectures
    </NuxtLink>

    <p class="section-label mb-2">Administration</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Nouvelle lecture</h1>

    <form class="space-y-5" @submit.prevent="soumettre">
      <div v-if="auth.role === 'super_admin'">
        <label class="block text-sm font-medium mb-1">Paroisse</label>
        <select
          v-model="paroisseId"
          required
          class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        >
          <option value="" disabled>Sélectionner une paroisse</option>
          <option v-for="p in paroisses" :key="p.id" :value="p.id">{{ p.nom }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">Programme</label>
        <select
          v-model="programmeId"
          required
          class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        >
          <option value="" disabled>Sélectionner un programme</option>
          <option v-for="p in programmesFiltres" :key="p.id" :value="p.id">
            {{ p.titre }} — {{ formaterDate(p.date_heure) }}
          </option>
        </select>
        <p v-if="!programmesFiltres.length" class="text-xs text-muted mt-1">
          Aucun programme disponible pour cette paroisse. Créez-en un d'abord.
        </p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">Référence</label>
        <input
          v-model="reference"
          type="text"
          required
          placeholder="Ex. Jean 3:16-21"
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

      <button
        type="submit"
        :disabled="chargement"
        class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
      >
        {{ chargement ? 'Création...' : 'Créer la lecture' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse', 'resp_lecteurs'],
})

interface ProgrammeCulte {
  id: number
  titre: string
  date_heure: string
  paroisse_id: number
}

const auth = useAuthStore()
const { paroisses } = useParoisses()
const { request } = useApi()

const paroisseId = ref<number | ''>('')
const programmeId = ref<number | ''>('')
const reference = ref('')
const dateLecture = ref('')
const texte = ref('')
const erreur = ref('')
const chargement = ref(false)

const { data: tousLesProgrammes } = await useAsyncData(
  'admin-lectures-tous-programmes',
  () => request<ProgrammeCulte[]>('/programmes?limit=200')
)

const paroisseCible = computed(() =>
  auth.role === 'super_admin' ? paroisseId.value : auth.user?.paroisse_id
)

const programmesFiltres = computed(() => {
  const liste = tousLesProgrammes.value ?? []
  if (!paroisseCible.value) return []
  return liste.filter((p) => p.paroisse_id === paroisseCible.value)
})

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

async function soumettre() {
  erreur.value = ''
  chargement.value = true
  try {
    const cible = paroisseCible.value
    if (!cible) {
      erreur.value = "Aucune paroisse associée à ce compte."
      return
    }
    if (!programmeId.value) {
      erreur.value = "Sélectionnez un programme."
      return
    }

    const lecture = await request<{ id: number }>('/lectures', {
      method: 'POST',
      body: {
        reference: reference.value,
        texte: texte.value || undefined,
        date_lecture: new Date(dateLecture.value).toISOString(),
        programme_id: programmeId.value,
        paroisse_id: cible,
      },
    })

    await navigateTo(`/admin/lectures/${lecture.id}`)
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}
</script>