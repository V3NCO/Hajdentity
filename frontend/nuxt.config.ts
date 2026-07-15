// https://nuxt.com/docs/api/configuration/nuxt-config
import { createResolver } from "nuxt/kit"
const { resolve } = createResolver(import.meta.url)

const apiProxyTarget = import.meta.env.NUXT_API_PROXY_TARGET ?? 'http://127.0.0.1:6532'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  css: ['~/assets/css/fonts.css', '~/assets/css/loading.css'],
  devtools: {
    enabled: true,

    timeline: {
      enabled: true
    }
  },

  vite: {
    optimizeDeps: {
      include: [
        '@vue/devtools-core',
        '@vue/devtools-kit',
        'openapi-fetch',
      ]
    }
  },

  routeRules: {
    '/api/**': {
      proxy: `${apiProxyTarget}/api/**`
    },
    '/fastapi/docs': { proxy: `${apiProxyTarget}/scalar` },
    '/openapi.json': { proxy: `${apiProxyTarget}/openapi.json` },
  },

  icon: {
    localApiEndpoint: '/_nuxt_icon_api',
    customCollections: [
      {
        prefix: 'hajdentity',
        dir: resolve('./app/assets/icons'),
      },
    ],

  },

  modules: ['@nuxt/icon'],

  runtimeConfig: {
    public: {
      apiBase: ''
    }
  }
})
