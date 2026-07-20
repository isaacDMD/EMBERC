<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/evenements" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux événements
    </NuxtLink>

    <p class="section-label mb-2">Administration</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Nouvel événement</h1>

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
        <label class="block text-sm font-medium mb-1">Type d'événement</label>
        <select
          v-model="typeEvenement"
          class="w-full rounded border border-ink/15 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary"
        >
          <option v-for="t in typesEvenement" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
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
        <label class="block text-sm font-medium mb-1">Affiche (optionnel)</label>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          class="w-full text-sm"
          @change="onFichierChange"
        />
        <p v-if="fichierAffiche" class="text-xs text-muted mt-1">{{ fichierAffiche.name }}</p>
      </div>

      <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>

      <button
        type="submit"
        :disabled="chargement"
        class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
      >
        {{ chargement ? statutChargement : "Créer l'événement" }}
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

const typesEvenement = [
  { value: 'conference', label: 'Conférence' },
  { value: 'semaine_de_la_jeunesse', label: 'Semaine de la jeunesse' },
  { value: 'semaine_des_femmes', label: 'Semaine des femmes' },
  { value: 'formation', label: 'Formation' },
  { value: 'concert', label: 'Concert' },
  { value: 'evangelisation', label: 'Évangélisation' },
]

const auth = useAuthStore()
const { paroisses } = useParoisses()
const { request } = useApi()

const titre = ref('')
const paroisseId = ref<number | ''>('')
const typeEvenement = ref('conference')
const dateDebut = ref('')
const dateFin = ref('')
const lieu = ref('')
const description = ref('')
const fichierAffiche = ref<File | null>(null)

function onFichierChange(event: Event) {
  const input = event.target as HTMLInputElement
  fichierAffiche.value = input.files?.[0] ?? null
}
const erreur = ref('')
const chargement = ref(false)

const { uploaderFichier } = useMediaUpload()
const statutChargement = ref('Création...')

async function soumettre() {
  erreur.value = ''
  chargement.value = true
  try {
    const cible = auth.role === 'super_admin' ? paroisseId.value : auth.user?.paroisse_id
    if (!cible) {
      erreur.value = "Aucune paroisse associée à ce compte."
      return
    }

    let image_url: string | undefined
    if (fichierAffiche.value) {
      statutChargement.value = "Envoi de l'affiche..."
      image_url = await uploaderFichier(fichierAffiche.value, 'image', Number(cible))
    }

    statutChargement.value = "Création..."
    const evenement = await request<{ id: number }>('/evenements', {
      method: 'POST',
      body: {
        titre: titre.value,
        description: description.value || undefined,
        date_debut: dateDebut.value,
        date_fin: dateFin.value,
        lieu: lieu.value || undefined,
        image_url,
        type_evenement: typeEvenement.value,
        paroisse_id: cible,
      },
    })

    await navigateTo(`/admin/evenements/${evenement.id}`)
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}
</script>