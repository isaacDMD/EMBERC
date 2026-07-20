<template>
  <div>
    <NuxtLink to="/programmes" class="text-sm text-primary hover:underline mb-6 inline-block">
      ← Retour aux programmes
    </NuxtLink>

    <div v-if="pending" class="text-muted text-sm">Chargement...</div>

    <div v-else-if="error" class="text-sm text-red-600">Ce programme est introuvable.</div>

    <div v-else-if="programme">
      <p class="section-label mb-2">{{ formaterDateHeure(programme.date_heure) }}</p>
      <h1 class="font-display text-3xl font-semibold mb-2">{{ programme.titre }}</h1>
      <p class="text-muted mb-6">
        {{ programme.type_culte }}
        <span v-if="programme.predicateur"> · Prédicateur : {{ programme.predicateur }}</span>
      </p>

      <div class="divider mb-6" />

      <h2 class="section-label mb-3">Chants du programme</h2>

      <div v-if="chantsPending" class="text-muted text-sm">Chargement des chants...</div>
      <p v-else-if="!chants?.length" class="text-muted text-sm mb-6">
        Aucun chant n'a encore été programmé.
      </p>
      <ol v-else class="flex flex-col gap-2 mb-6">
        <li
          v-for="item in chants"
          :key="item.id"
          class="flex items-center gap-3 bg-surface border border-ink/10 rounded-lg px-4 py-3"
        >
          <span class="text-sm text-muted w-6">{{ item.ordre }}.</span>
          <span class="font-medium">{{ item.titre }}</span>
          <span class="text-xs text-muted ml-auto">N° {{ item.numero }}</span>
        </li>
      </ol>

      <h2 class="section-label mb-3">Lectures bibliques</h2>

      <div v-if="lecturesPending" class="text-muted text-sm">Chargement des lectures...</div>
      <p v-else-if="!lectures?.length" class="text-muted text-sm">
        Aucune lecture n'a encore été ajoutée.
      </p>
      <div v-else class="flex flex-col gap-2">
        <div
          v-for="lecture in lectures"
          :key="lecture.id"
          class="bg-surface border border-ink/10 rounded-lg px-4 py-3"
        >
          <p class="font-medium">{{ lecture.reference }}</p>
          <p v-if="lecture.texte" class="text-sm text-muted mt-1 whitespace-pre-line">
            {{ lecture.texte }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ProgrammeCulte {
  id: number
  titre: string
  type_culte: string
  predicateur?: string | null
  date_heure: string
}

interface ChantDansProgramme {
  id: number
  chant_id: number
  ordre: number
  titre: string
  numero: string
}

interface Lecture {
  id: number
  reference: string
  texte?: string | null
}

const route = useRoute()
const { request } = useApi()

const { data: programme, pending, error } = await useAsyncData(
  `programme-${route.params.id}`,
  () => request<ProgrammeCulte>(`/programmes/${route.params.id}`)
)

const { data: chants, pending: chantsPending } = await useAsyncData(
  `programme-${route.params.id}-chants`,
  () => request<ChantDansProgramme[]>(`/programmes/${route.params.id}/chants`)
)

const { data: lectures, pending: lecturesPending } = await useAsyncData(
  `programme-${route.params.id}-lectures`,
  () => request<Lecture[]>(`/lectures?programme_id=${route.params.id}`)
)

function formaterDateHeure(iso: string) {
  const date = new Date(iso)
  return date.toLocaleString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>