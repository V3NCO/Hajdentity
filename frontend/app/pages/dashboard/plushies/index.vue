<script setup lang="ts">
import { useApi } from '~/lib/api'

useSeoMeta({
  title: 'Plushies',
  ogTitle: 'Plushies',
  ogUrl: 'https://id.blahaj.engineering/dashboard/plushies',
  twitterTitle: 'Plushies',
  twitterCard: 'summary'
})

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
  <div>
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
  </div>
</template>

<style>
.cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  padding: 1.5em

}

.card {
  display: block;
  font-family: "Noto Sans";
  aspect-ratio: 4 / 3;
  margin: 0.35em;
  text-decoration: none;
  background-size: cover;
  background-position: center;
  border-radius: 2em;
  overflow: hidden;
}

.gradient {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  height: 100%;
  width: 100%;
  padding: 1.25rem;
  box-sizing: border-box;
  background: radial-gradient(ellipse at bottom left,rgba(0,0,0,.9) 0%,rgba(0,0,0,.6) 50%,transparent 100%);
  color: #DDD;
}

.gradient h1 {
  margin: 0 0 0.25rem 0;
}

.gradient p {
  margin: 0;
  font-weight: 300;
}

.gradient span {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.new {
  color: dimgray;
  border: 2px dashed gray;
  display: grid;
  justify-items: center;
}

.new p {
  margin: 0;
  font-size: 1.25rem;
}

.plus {
  font-size: 3rem;
  align-self: flex-end;
}

html, body {
  height: 100%;
  margin: 0;
}
</style>
