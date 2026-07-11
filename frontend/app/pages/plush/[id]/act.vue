<script setup lang="ts">
import { useApi } from '~/lib/api'

useHead({ htmlAttrs: { lang: 'en' }})
const api = useApi()
const route = useRoute()

const loading = ref(true)

const plushdata = ref()
const sharkeydata = ref()
const plusherror = ref()

onMounted(async () => {
  const { data: hajData, error: err } = await api.GET(
    '/api/hajs/{haj_id}',
    { params: { path: { haj_id: route.params.id as string } } }
  )
  plushdata.value = hajData?.haj
  sharkeydata.value = hajData?.sharkey
  plusherror.value = err
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
<div class="midcont" v-if="!loading">
  <div class="act-topline">
    <div class="act-pfp" :style="{ backgroundImage: `url(/api/hajs/${route.params.id}/pfp)` }"></div>
    <div class="act-title">
       <h1>{{plushdata?.displayname}} <span class="act-pronouns">{{plushdata?.pronouns}}</span></h1>
       <h2 class="act-username">@{{plushdata?.username}}</h2>
       <p>{{plushdata?.description}}</p>
    </div>
  </div>
  <div class="buttons">
    <a :href="`/plush/${route.params.id}/friend`" class="button">
      <Icon name="material-symbols:person-add-outline" />
      <h1>Add Friend</h1>
      <h3>{{plushdata?.displayname}} met a new plush friend?<br/>Add them!</h3>
    </a>
    <a :href="`/plush/${route.params.id}/post`" class="button">
      <Icon name="material-symbols:history-edu" />
      <h1>New Memory</h1>
      <h3>You and {{plushdata?.displayname}} made a memory?<br/>Share it :3</h3>
    </a>
    <a :href="`/plush/${route.params.id}`" class="button">
      <Icon name="hajdentity:logo-material-padding" />
      <h1>See Profile</h1>
      <h3>Hi! Learn more about who {{plushdata?.displayname}} is here ^-^</h3>
    </a>
  </div>
</div>
</template>

<style>
html, body {
  height: 100%;
  margin: 0;
}

body {
  overflow: hidden;
  background-color: #212121;
  background-repeat: no-repeat;
  background-size: cover;
}

#app, #__nuxt {
  height: 100%;
  display: flex;
  justify-content: center;
}

.midcont {
  display: flex;
  flex-direction: column;
  font-family:  "Space Grotesk";
  height:100svh;
  width: 100vw;
  max-width: 50rem;
  box-sizing: border-box;
  gap: 3em;
  padding: 2em;
}

.act-topline {
  display: flex;
  flex-direction: row;
  height: 17.5svh;
  max-height: 17.5svh;
  gap: 2rem;
  font-weight: 500;
}

.act-topline h1 {
  font-size: 2.5rem;
  color: #E3E3E3;
  gap: 1rem;
  margin: 0;
}

.act-topline p {
  font-size: 1rem;
  color: #E3E3E3;
  margin: 0;
  font-weight: 400;
}

.act-pronouns {
  font-family: "Montserrat";
  font-weight: 400;
  font-size: 1.5rem;
}

.act-title {
  display:flex;
  flex-direction:column;
  overflow: hidden;
}

.act-username {
  font-family: "Space Grotesk";
  font-weight: 300;
  color: #E3E3E3;
  font-size: 1.5rem;
  margin-top: 0;
}

.act-pfp {
  outline: 0.4em solid #638FAC;
  aspect-ratio: 1 / 1;
  background-size: cover;
  background-position: center;
  border-radius: 35px;
}

.buttons {
  display: grid;
  grid-auto-rows: 1fr;
  box-sizing: border-box;
  gap: 1.5em;
  height: 100%;
}

.button {
  display: grid;
  width: 100%;
  border-radius: 35px;
  background-color: #2D2D2D;
  outline: 0.2rem solid #404040;
  box-sizing: border-box;
  justify-content: center;
  align-content: center;
  color: #E3E3E3;
  text-decoration: none;
  text-align: center;
  gap: 0.2em;
}

.button h1 {
  margin: 0;
  font-family: "Space Grotesk";
  font-weight: 500;
  font-size: 1.5rem;
  justify-content: center;
}

.button h3 {
  margin: 0;
  color: #636363;
  font-family: "Oswald";
  font-weight: 400;
  font-size: 1.1rem;
}

.iconify {
  justify-self: center;
  width: 3rem;
  height: 3rem;
}


@media screen and (max-width: 500px) {
  .act-topline {
    height: 15svh;
    max-height: 15svh;
    gap: 2rem;
    font-weight: 500;
  }

  .act-topline h1 {
    font-size: 1.5rem;
    color: #E3E3E3;
    gap: 1rem;
    margin: 0;
  }

  .act-pfp {
    aspect-ratio: 1 / 1;
    border-radius: 20px;
  }

  .act-username {
    font-family: "Space Grotesk";
    font-weight: 300;
    color: #E3E3E3;
    font-size: 1.2rem;
    margin-top: 0;
  }

  .act-pronouns {
    font-size: 0.9rem;
  }
}
</style>
