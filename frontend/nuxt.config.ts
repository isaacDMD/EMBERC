export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@nuxtjs/google-fonts'],
  googleFonts: {
    families: {
      Fraunces: [500, 600, 700],
      Inter: [400, 500, 600, 700],
    },
    display: 'swap',
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000/api/v1',
    },
  },
  app: {
    head: {
      title: 'EMBERC',
      htmlAttrs: { lang: 'fr' },
    },
  },
})