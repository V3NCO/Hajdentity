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


useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: { style: 'overflow: hidden; background-color: #212121; background-repeat: no-repeat; background-size: cover;' }
})
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
  <div class="leftcont">
    <div class="sidebar">
      <a href="./"><Icon class="beeg" name="material-symbols:account-circle"/></a>
      <hr/>
      <a href="#"><Icon class="beeg" name="hajdentity:haj"/></a>
    </div>
  </div>
  <div class="rightcont">
    <div class="cards">
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
  </div>
</template>

<style scoped>
.cards {
  background-color: #2D2D2D;
  box-sizing: border-box;
  height: 100%;
  border-radius: 18px;
}

.leftcont {
  float: left;
  height: 100svh;
  padding: 1rem;
  box-sizing: border-box;
}

.rightcont {
  height: 100svh;
  width: 100%;
  padding: 1rem;
  box-sizing: border-box;
}

.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
  width: 4rem;
  padding: 0.75rem;
  background-color:#2D2D2D;
  border-radius: 18px;
  gap: 0.75rem;
}

.sidebar a {
  width: 100%;
  aspect-ratio: 1/1;
  box-sizing: border-box;
  color: #E3E3E3;
  text-decoration: none;
}

.sidebar hr {
  margin: 0;
  box-sizing: border-box;
}

.beeg {
  height: 100%;
  width: 100%;
}
</style>
