// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: {
    enabled: true,

    timeline: {
      enabled: true
    }
  },
  routeRules: {
      '/api/**': {
        proxy: "http://127.0.0.1:8000/api/**"
      },
      '/fastapi/docs': { proxy: "http://127.0.0.1:8000/docs" },
      '/openapi.json': { proxy: "http://127.0.0.1:8000/openapi.json" }
    }
})