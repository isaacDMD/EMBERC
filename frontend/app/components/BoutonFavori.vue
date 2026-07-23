<template>
  <ClientOnly>
    <button
      v-if="auth.estConnecte"
      type="button"
      class="inline-flex items-center gap-1 text-sm transition"
      :class="estActif ? 'text-accent-dark' : 'text-muted hover:text-accent-dark'"
      :disabled="enCours"
      @click.stop.prevent="basculer"
    >
      <span>{{ estActif ? '★' : '☆' }}</span>
      <span v-if="avecLabel">{{ estActif ? 'Favori' : 'Ajouter aux favoris' }}</span>
    </button>
  </ClientOnly>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

const props = defineProps<{
  type: 'annonce' | 'evenement' | 'media' | 'chant' | 'article'
  itemId: number
  avecLabel?: boolean
}>()

const auth = useAuthStore()
const { charge, chargerFavoris, estFavori, basculerFavori } = useFavoris()
const enCours = ref(false)

onMounted(() => {
  if (auth.estConnecte && !charge.value) {
    chargerFavoris()
  }
})

const estActif = computed(() => estFavori(props.type, props.itemId))

async function basculer() {
  enCours.value = true
  try {
    await basculerFavori(props.type, props.itemId)
  } finally {
    enCours.value = false
  }
}
</script>