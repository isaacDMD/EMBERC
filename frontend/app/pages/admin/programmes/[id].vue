<template>
  <div class="max-w-2xl">
    <NuxtLink to="/admin/programmes" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux programmes
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>
    <div v-else-if="error" class="text-sm text-red-600">Ce programme est introuvable.</div>

    <template v-else-if="programme">
      <div class="flex items-center justify-between mb-6">
        <div>
            <p class="section-label mb-2">Administration</p>
            <h1 class="font-display text-3xl font-semibold">{{ programme.titre }}</h1>
            <p class="text-sm text-muted mt-1">{{ formaterDateHeure(programme.date_heure) }}</p>
        </div>
        <button
            v-if="peutModifier"
            class="text-xs px-3 py-1.5 rounded-full transition"
            :class="programme.publie ? 'bg-green-100 text-green-800' : 'bg-ink/5 text-muted hover:bg-ink/10'"
            @click="basculerPublication"
        >
            {{ programme.publie ? 'Publié — dépublier' : 'Brouillon — publier' }}
        </button>
        </div>

        <form v-if="peutModifier" class="space-y-5 mb-10" @submit.prevent="soumettre">
        <!-- ... tous les champs existants, inchangés ... -->
        </form>

      <form class="space-y-5 mb-10" @submit.prevent="soumettre">
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
          <label class="block text-sm font-medium mb-1">Type de culte</label>
          <select
            v-model="typeCulte"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          >
            <option v-for="c in typesCulte" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Date et heure</label>
          <input
            v-model="dateHeure"
            type="datetime-local"
            required
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Prédicateur (optionnel)</label>
          <input
            v-model="predicateur"
            type="text"
            class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
          />
        </div>

        <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>
        <p v-if="succes" class="text-sm text-green-700">Programme mis à jour.</p>

        <button
          type="submit"
          :disabled="chargement"
          class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
        >
          {{ chargement ? 'Enregistrement...' : 'Enregistrer les modifications' }}
        </button>
      </form>

      <div class="divider mb-6" />

      <h2 class="section-label mb-3">Chants programmés</h2>

      <div v-if="chantsPending" class="text-muted text-sm mb-4">Chargement...</div>
      <ol v-else class="flex flex-col gap-2 mb-4">
        <li
          v-for="item in chantsProgrammes"
          :key="item.id"
          class="flex items-center gap-3 bg-surface border border-ink/10 rounded-lg px-4 py-2"
        >
          <span class="text-sm text-muted w-6">{{ item.ordre }}.</span>
          <span class="font-medium flex-1">{{ item.titre }}</span>
          <button class="text-sm text-red-600 hover:underline" @click="retirerChant(item.chant_id)">
            Retirer
          </button>
        </li>
        <li v-if="!chantsProgrammes?.length" class="text-muted text-sm">Aucun chant programmé.</li>
      </ol>

      <form class="flex flex-col sm:flex-row gap-2" @submit.prevent="ajouterChant">
        <select
          v-model="chantIdASelectionner"
          class="flex-1 rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        >
          <option value="" disabled>Choisir un chant</option>
          <option v-for="c in tousLesChants" :key="c.id" :value="c.id">{{ c.numero }} — {{ c.titre }}</option>
        </select>
        <button
          type="submit"
          class="bg-primary/10 text-primary rounded px-4 py-2 text-sm font-medium hover:bg-primary/20 transition"
        >
          Ajouter
        </button>
      </form>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse', 'resp_musical'],
})
const auth = useAuthStore()
const peutModifier = computed(() => ['super_admin', 'admin_paroisse'].includes(auth.role ?? ''))

function formaterDateHeure(iso: string) {
  return new Date(iso).toLocaleString('fr-FR', {
    weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit',
  })
}

interface ProgrammeCulte {
  id: number
  titre: string
  type_culte: string
  predicateur?: string | null
  date_heure: string
  publie: boolean
}

interface ChantDansProgramme {
  id: number
  chant_id: number
  ordre: number
  titre: string
}

interface Chant {
  id: number
  numero: string
  titre: string
}

const typesCulte = [
  "Messe du dimanche", "Prière de bénédiction", "Prière de délivrance",
  "Messe d'anniversaire", "Pâques", "Pentecôte", "Noël", "Nouvel An",
  "Veille de Noël", "Messe d'action de grâce",
]

const route = useRoute()
const { request } = useApi()

const { data: programme, pending, error, refresh } = await useAsyncData(
  `admin-programme-${route.params.id}`,
  () => request<ProgrammeCulte>(`/programmes/${route.params.id}`)
)

const { data: chantsProgrammes, pending: chantsPending, refresh: refreshChants } = await useAsyncData(
  `admin-programme-${route.params.id}-chants`,
  () => request<ChantDansProgramme[]>(`/programmes/${route.params.id}/chants`)
)

const { data: tousLesChants } = await useAsyncData(
  'admin-tous-les-chants',
  () => request<Chant[]>('/chants?limit=200')
)

const titre = ref('')
const typeCulte = ref('')
const dateHeure = ref('')
const predicateur = ref('')
const erreur = ref('')
const succes = ref(false)
const chargement = ref(false)
const chantIdASelectionner = ref<number | ''>('')

function isoVersDatetimeLocal(iso: string) {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

watchEffect(() => {
  if (programme.value) {
    titre.value = programme.value.titre
    typeCulte.value = programme.value.type_culte
    dateHeure.value = isoVersDatetimeLocal(programme.value.date_heure)
    predicateur.value = programme.value.predicateur ?? ''
  }
})

async function soumettre() {
  erreur.value = ''
  succes.value = false
  chargement.value = true
  try {
    await request(`/programmes/${route.params.id}`, {
      method: 'PUT',
      body: {
        titre: titre.value,
        type_culte: typeCulte.value,
        date_heure: new Date(dateHeure.value).toISOString(),
        predicateur: predicateur.value || undefined,
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

async function basculerPublication() {
  if (!programme.value) return
  await request(`/programmes/${route.params.id}`, {
    method: 'PUT',
    body: { publie: !programme.value.publie },
  })
  await refresh()
}

async function ajouterChant() {
  if (!chantIdASelectionner.value) return
  const ordre = (chantsProgrammes.value?.length ?? 0) + 1
  await request(`/programmes/${route.params.id}/chants`, {
    method: 'POST',
    body: { chant_id: chantIdASelectionner.value, ordre },
  })
  chantIdASelectionner.value = ''
  await refreshChants()
}

async function retirerChant(chantId: number) {
  await request(`/programmes/${route.params.id}/chants/${chantId}`, { method: 'DELETE' })
  await refreshChants()
}
</script>