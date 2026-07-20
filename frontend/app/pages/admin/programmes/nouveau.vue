<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/programmes" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux programmes
    </NuxtLink>

    <p class="section-label mb-2">Administration</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Nouveau programme</h1>

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

      <button
        type="submit"
        :disabled="chargement"
        class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
      >
        {{ chargement ? 'Création...' : 'Créer le programme' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

definePageMeta({
  middleware: 'admin',
  rolesAutorises: ['super_admin', 'admin_paroisse'],
})

const typesCulte = [
  "Messe du dimanche",
  "Prière de bénédiction",
  "Prière de délivrance",
  "Messe d'anniversaire",
  "Pâques",
  "Pentecôte",
  "Noël",
  "Nouvel An",
  "Veille de Noël",
  "Messe d'action de grâce",
]

const auth = useAuthStore()
const { paroisses } = useParoisses()
const { request } = useApi()

const titre = ref('')
const paroisseId = ref<number | ''>('')
const typeCulte = ref(typesCulte[0])
const dateHeure = ref('')
const predicateur = ref('')
const erreur = ref('')
const chargement = ref(false)

async function soumettre() {
  erreur.value = ''
  chargement.value = true
  try {
    const cible = auth.role === 'super_admin' ? paroisseId.value : auth.user?.paroisse_id
    if (!cible) {
      erreur.value = "Aucune paroisse associée à ce compte."
      return
    }

    const programme = await request<{ id: number }>('/programmes', {
      method: 'POST',
      body: {
        titre: titre.value,
        type_culte: typeCulte.value,
        date_heure: new Date(dateHeure.value).toISOString(),
        predicateur: predicateur.value || undefined,
        paroisse_id: cible,
      },
    })

    await navigateTo(`/admin/programmes/${programme.id}`)
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}
</script>