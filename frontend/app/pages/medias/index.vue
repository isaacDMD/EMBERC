<template>
  <div>
    <p class="section-label mb-2">Bibliothèque</p>
    <h1 class="font-display text-3xl font-semibold mb-6">Médias</h1>

    <div class="flex flex-wrap items-center gap-2 mb-6">
      <button
        v-for="option in types"
        :key="option.value ?? 'tous'"
        class="px-3 py-1.5 rounded-full text-sm border transition"
        :class="typeActif === option.value
          ? 'bg-primary text-white border-primary'
          : 'border-ink/15 text-muted hover:border-primary/40 hover:text-primary'"
        @click="basculerType(option.value)"
      >
        {{ option.label }}
      </button>
    </div>

    <div class="divider mb-6" />

    <div v-if="pending" class="text-muted text-sm">Chargement des médias...</div>

    <div v-else-if="error" class="text-sm text-red-600">
      Impossible de charger les médias pour le moment.
    </div>

    <div v-else-if="!medias?.length" class="text-muted text-sm">
      Aucun média disponible pour l'instant.
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <article
        v-for="media in medias"
        :key="media.id"
        class="bg-surface border border-ink/10 rounded-lg overflow-hidden flex flex-col"
      >
        <img
          v-if="media.type_media === 'image'"
          :src="media.url_media"
          :alt="media.titre"
          class="w-full h-48 object-cover"
        />
        <img
          v-else-if="media.thumbnail_url"
          :src="media.thumbnail_url"
          :alt="media.titre"
          class="w-full h-48 object-cover"
        />

        <div class="p-5 flex flex-col gap-2 flex-1">
          <span class="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary self-start">
            {{ libelleType(media.type_media) }}
          </span>
          <h2 class="font-display text-lg font-semibold">{{ media.titre }}</h2>
          <BoutonFavori type="media" :item-id="media.id" />
          <p v-if="media.description" class="text-sm text-muted">{{ media.description }}</p>

          <audio
            v-if="media.type_media === 'audio'"
            :src="media.url_media"
            controls
            class="w-full mt-1"
          />
          <video
            v-else-if="media.type_media === 'video'"
            :src="media.url_media"
            controls
            class="w-full mt-1 rounded"
          />
          <a 
            v-else-if="media.type_media === 'document'"
            :href="media.url_media"
            target="_blank"
            rel="noopener"
            class="text-sm font-medium text-primary hover:underline mt-auto"
          >
            Ouvrir le document ↗
          </a>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Media {
  id: number
  titre: string
  type_media: 'audio' | 'video' | 'image' | 'document'
  description?: string | null
  url_media: string
  thumbnail_url?: string | null
  duree_secondes?: number | null
}

const types = [
  { value: null, label: 'Tous' },
  { value: 'audio', label: 'Audio' },
  { value: 'video', label: 'Vidéo' },
  { value: 'image', label: 'Photo' },
  { value: 'document', label: 'Document' },
]

function libelleType(valeur: string) {
  return types.find((t) => t.value === valeur)?.label ?? valeur
}

const { request } = useApi()
const typeActif = ref<string | null>(null)

function basculerType(valeur: string | null) {
  typeActif.value = valeur
}

const { data: medias, pending, error } = await useAsyncData(
  'medias-liste',
  () => {
    const suffixe = typeActif.value ? `&type_media=${typeActif.value}` : ''
    return request<Media[]>(`/medias?publie=true&limit=50${suffixe}`)
  },
  { watch: [typeActif] }
)
</script>