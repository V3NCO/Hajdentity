<script setup lang="ts">
import { useApi } from '~/lib/api'

useSeoMeta({
  title: 'Plushies',
  ogTitle: 'Plushies',
  ogUrl: 'https://id.blahaj.engineering/dashboard/plushies',
  twitterTitle: 'Plushies',
  twitterCard: 'summary'
})

definePageMeta({ middleware: 'auth' })

const api = useApi()

const { data: plushies, error: err } = await api.GET('/api/haj/list')
</script>

<template>
</template>
