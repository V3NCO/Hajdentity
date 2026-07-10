<script setup lang="ts">
  import '~/assets/css/fonts.css'
  import loadingCss from '~/assets/css/loading.css?raw'
  import { useApi } from '~/lib/api'

  function formatCompactNumber(number: number) {
    if (number < 1000) {
      return number;
    } else if (number >= 1000 && number < 1000000) {
      return (number / 1000).toFixed(1) + "K";
    } else if (number >= 1000000 && number < 1000000000) {
      return (number / 1000000).toFixed(1) + "M";
    } else if (number >= 1000000000 && number < 1000000000000) {
      return (number / 1000000000).toFixed(1) + "B";
    }
  }

  useHead({ htmlAttrs: { lang: 'en' }, style: [{ textContent: loadingCss }] })
  const api = useApi()
  const route = useRoute()

  const loading = ref(true)

  const plushdata = ref()
  const postdata = ref()
  const sharkeydata = ref()
  const plusherror = ref()
  const postserror = ref()

  onMounted(async () => {
    const { data: hajData, error: err } = await api.GET(
      '/api/hajs/{haj_id}',
      { params: { path: { haj_id: route.params.id as string } } }
    )
    const { data: postsData, error: err2 } = await api.GET(
      '/api/hajs/{haj_id}/posts',
      { params: { path: { haj_id: route.params.id as string } } }
    )
    plushdata.value = hajData?.haj
    postdata.value = postsData?.posts
    sharkeydata.value = hajData?.sharkey
    plusherror.value = err
    postserror.value = err2
    loading.value = false
  })

  const likes = 13292;
  const views = 4343333;
</script>

<template>
<Transition><div v-if="loading" class="loading">
  <h1>Loading...</h1>
  <video autoplay loop muted playsinline>
    <source src="/blahaj.webm" type="video/webm">
  </video>
</div></Transition>

<div class="bento" v-if="!loading">
  <div class="tile">
    <h1 class="topline">{{plushdata.displayname}} <span class="pronouns">{{plushdata.pronouns}}</span> <span class="location">📍 {{plushdata.location}}</span></h1>
    <h2 class="username">@{{plushdata.username}}</h2>
    <p>{{plushdata.description}}</p>
  </div>
  <div class="tile" :style="{ backgroundImage: `url(/api/hajs/${postdata[0]?.haj}/posts/${postdata[0]?.id}/image)` }">
    <h1>Latest post:</h1>
    <h2>{{postdata[0]?.text}}</h2>
  </div>
  <div class="tile">
    <div class="stat">
      <h2>Likes</h2>
      <h1 style="background-image: radial-gradient(circle at top left, #FF4043 0, #992628 100%);">{{formatCompactNumber(likes)}}</h1>
    </div>
    <div class="stat">
      <h2>Views</h2>
      <h1 style="background-image: radial-gradient(circle at top left, #6CFF82 0, #41994E 100%);">{{formatCompactNumber(views)}}</h1>
    </div>
    <div class="stat">
      <h2>Posts</h2>
      <h1 style="background-image: radial-gradient(circle at top left, #0D76FF 0, #084799 100%);">{{formatCompactNumber(sharkeydata.notesCount)}}</h1>
    </div>
    <div class="stat">
      <h2>Followers</h2>
      <h1 style="background-image: radial-gradient(circle at top left, #AD41FF 0, #682799 100%);">{{formatCompactNumber(sharkeydata.followersCount)}}</h1>
    </div>
  </div>
  <div class="tile" :style="{ backgroundImage: `url(/api/hajs/${postdata[0]?.haj}/pfp)` }"></div>
  <div class="tile"></div>
  <div class="tile stat">
    <h2>Size</h2>
    <h1 style="background-image: radial-gradient(circle at top left, #FF9A41 0, #995C27 100%);">{{plushdata.size}}<span style="font-size: 2rem;">cm</span></h1>
  </div>
  <div class="tile stat">
    <h2>Gender</h2>
    <h3>{{plushdata.gender}}</h3>
  </div>
  <div class="tile"></div>
  <div class="tile"></div>
  <div class="tile"></div>
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
  font-family: "Noto Sans";
  background-repeat: no-repeat;
  background-size: cover;
}

#app, #__nuxt {
  height: 100%;
}


.bento {
  display: grid;
  font-family:  "Space Grotesk";
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(5, 1fr);
  height:100svh;
  width: 100vw;
  box-sizing: border-box;
  gap: 1em;
  padding: 1em;
}

.tile {
  grid-column: span 1;
  padding: 1.3em;
  color: #E3E3E3;
  box-sizing: border-box;
  grid-row: span 1;
  border-radius: 35px;
  background-color: #2D2D2D;
  height: 100%;
  width: 100%;
}

.stat {
  grid-column: span 1;
  padding: 1.3em;
  color: #E3E3E3;
  box-sizing: border-box;
  grid-row: span 1;
  border-radius: 35px;
  background-color: #2D2D2D;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.stat h2 {
  font-family: "Space Grotesk";
  font-weight: 500;
  margin: 0;
  font-size: 1.5rem;
  position: absolute;
  top: 1em;
  left: 1em;
}

.stat h3 {
  font-family: "Space Grotesk";
  font-weight: 400;
  font-size: 2rem;
}

.stat h1 {
  font-family: "Montserrat";
  font-weight: 900;
  margin: 0;
  font-size: 5rem;
  color: transparent;
  background-clip: text;
}

.topline {
  font-size: 2.5rem;
  margin: 0;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5em;
}

.username {
  font-family: "Space Grotesk";
  font-weight: 300;
  font-size: 1.5rem;
  margin-top: 0;
}

.location {
  font-family: "Montserrat";
  font-weight: 400;
  font-size: 1.5rem;
  margin-left: auto;
}

.pronouns {
  font-family: "Montserrat";
  font-weight: 400;
  font-size: 1.5rem;
}


.tile:nth-child(1) {
  grid-column:  1 / 5;
  grid-row: 1 / 3;
}

.tile:nth-child(2) {
  grid-column:  5 / 8;
  grid-row: 1 / 4;
  font-family: "Oswald";
  font-weight: 400;
  position: relative;
  background-size: cover;
}

.tile:nth-child(2) h1 {
  margin: 0.25em;
  font-family: "Oswald";
  font-weight: 400;
}

.tile:nth-child(2) h2 {
  margin: 0.25em;
  font-family: "Oswald";
  font-weight: 400;
  position: absolute;
  bottom: 1.3rem;
}

.tile:nth-child(3) {
  grid-column:  1 / 4;
  grid-row: 3 / 6;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  background-color: #212121;
  padding: 0;
  gap: 1em;
}

/* PFP in middle */
.tile:nth-child(4) {
  grid-column:  4;
  grid-row: 3;
  outline: 0.4em solid #638FAC;
  background-size: cover;
  background-position: center;
}

.tile:nth-child(5) {
  grid-column:  4;
  grid-row: 4 / 6;
}

.tile:nth-child(6) {
  grid-column:  5;
  grid-row: 4;
}

.tile:nth-child(6) h1 {
  font-size: 3rem;
}

.tile:nth-child(7) {
  grid-column:  6 / 8;
  grid-row: 4;
}

.tile:nth-child(8) {
  grid-column:  5;
  grid-row: 5;
}

.tile:nth-child(9) {
  grid-column:  6;
  grid-row: 5;
}
</style>
