<script setup lang="ts">
useSeoMeta({
  title: 'Register',
  description: 'Make a new account on Hajdentity!',
  ogTitle: 'Register',
  ogDescription: 'Make a new account on Hajdentity!',
  ogImage: '[og:image]',
  ogUrl: 'https://id.blahaj.engineering/register',
  twitterTitle: 'Register',
  twitterDescription: 'Make a new account on Hajdentity!',
  twitterImage: '[twitter:image]',
  twitterCard: 'summary'
})

useHead({
  htmlAttrs: {
    lang: 'en'
  },
  link: [
    {
      rel: 'icon',
      type: 'image/png',
      href: '/favicon.png'
    }
  ]
})
</script>

<template>
  <input id="username">
  <input id="email">
  <input id="password" type="password">
  <input id="confirm-password" type="password">
</template>
