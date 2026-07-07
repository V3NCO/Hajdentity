<script setup lang="ts">
import cardsCss from '~/assets/css/cards.css?raw'
import loadingCss from '~/assets/css/loading.css?raw'
import { useApi } from '~/lib/api'

useSeoMeta({
  title: 'Plushies',
  ogTitle: 'Plushies',
  ogUrl: 'https://id.blahaj.engineering/dashboard/plushies',
  twitterTitle: 'Plushies',
  twitterCard: 'summary'
})


useHead({ htmlAttrs: { lang: 'en' }, style: [{ textContent: loadingCss }, { textContent: cardsCss }] })
definePageMeta({ middleware: 'auth', ssr: false })

const api = useApi()
const loading = ref(true)
const data = ref()
const error = ref()
onMounted(async () => {
  const { data: plushies, error: err } = await api.GET('/api/haj/list')
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
      :style="{ backgroundImage: `url(/api/haj/image/${plush.uuid})` }"
      v-for="plush in data?.hajs"
      :key="plush.uuid"
      class="card"
      :href="`/dashboard/plushies/${plush.uuid}`"
    >
      <div class="gradient">
        <h1>{{ plush.name }}</h1>
        <span>
          <Icon v-if="plush.public" name="material-symbols:public" title="Public"/>
          <Icon v-else name="material-symbols:lock" title="Private"/>
          <p>{{ plush.pronouns }}</p>
        </span>
      </div>
    </a>
  </div>
</template>
