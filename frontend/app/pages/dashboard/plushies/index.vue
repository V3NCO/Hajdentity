<script setup lang="ts">
import '~/assets/css/cards.css'
import { useApi } from '~/lib/api'

useSeoMeta({
  title: 'Plushies',
  ogTitle: 'Plushies',
  ogUrl: 'https://id.blahaj.engineering/dashboard/plushies',
  twitterTitle: 'Plushies',
  twitterCard: 'summary'
})


useHead({ htmlAttrs: { lang: 'en' }})
definePageMeta({ middleware: 'auth', ssr: false })

const api = useApi()
const loading = ref(true)
const data = ref()
const error = ref()
onMounted(async () => {
  const { data: plushies, error: err } = await api.GET('/api/hajs')
  data.value = plushies
  error.value = err
  loading.value = false
})
</script>

<template>
  <Transition><div v-if="loading" class="loading">
    <h1>Loading...</h1>
    <video autoplay loop muted playsinline>
      <source src="/blahaj.webm" type="video/webm">
    </video>
  </div></Transition>
  <div v-if="error && !loading">Error: {{ error }}</div>
  <div v-else class="cards">
    <a href="/dashboard/plushies/new" class="card new">
      <Icon name="material-symbols:add" class="plus" />
      <p>Add plushie</p>
    </a>
    <a
      :style="{ backgroundImage: `url(/api/hajs/${plush.uuid}/image)` }"
      v-for="plush in data?.hajs"
      :key="plush.uuid"
      class="card"
      :href="`/dashboard/plushies/${plush.uuid}`"
    >
      <div class="gradient">
        <h1>{{ plush.displayname }}</h1>
        <span>
          <p>{{ plush.pronouns }}</p>
        </span>
      </div>
    </a>
  </div>
</template>
