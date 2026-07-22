<template>
  <div class="max-w-xl">
    <NuxtLink to="/admin/actualites" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux actualités
    </NuxtLink>

    <p class="section-label mb-2">Administration</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Nouvelle actualité</h1>

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
        <label class="block text-sm font-medium mb-1">Image (optionnel)</label>
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          class="w-full text-sm"
          @change="onFichierChange"
        />
        <p v-if="fichier" class="text-xs text-muted mt-1">{{ fichier.name }}</p>
      </div>

      <p v-if="erreur" class="text-sm text-red-600">{{ erreur }}</p>

      <button
        type="submit"
        :disabled="chargement"
        class="bg-primary text-white rounded px-5 py-2.5 text-sm font-medium hover:bg-primary-dark transition disabled:opacity-60"
      >
        {{ chargement ? statutChargement : "Créer l'actualité" }}
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

const auth = useAuthStore()
const { paroisses } = useParoisses()
const { request } = useApi()
const { uploaderFichier } = useMediaUpload()

const titre = ref('')
const paroisseId = ref<number | ''>('')
const resume = ref('')
const contenu = ref('')
const fichier = ref<File | null>(null)
const erreur = ref('')
const chargement = ref(false)
const statutChargement = ref('Création...')

function onFichierChange(event: Event) {
  const input = event.target as HTMLInputElement
  fichier.value = input.files?.[0] ?? null
}

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
    if (fichier.value) {
      statutChargement.value = "Envoi de l'image..."
      image_url = await uploaderFichier(fichier.value, 'image', Number(cible))
    }

    statutChargement.value = "Création..."
    const actualite = await request<{ id: number }>('/actualites', {
      method: 'POST',
      body: {
        titre: titre.value,
        resume: resume.value || undefined,
        contenu: contenu.value,
        image_url,
        paroisse_id: cible,
      },
    })

    await navigateTo(`/admin/actualites/${actualite.id}`)
  } catch (e: any) {
    erreur.value = e?.data?.detail || "Une erreur est survenue."
  } finally {
    chargement.value = false
  }
}
</script>