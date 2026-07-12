<script setup lang="ts">
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

  function timeAgo(dateStr: string) {
    const now = new Date()
    const d = new Date(dateStr)
    const diff = now.getTime() - d.getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return 'just now'
    if (mins < 60) return mins + 'm ago'
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return hrs + 'h ago'
    const days = Math.floor(hrs / 24)
    if (days < 30) return days + 'd ago'
    const months = Math.floor(days / 30)
    if (months < 12) return months + 'mo ago'
    const years = Math.floor(months / 12)
    return years + 'y ago'
  }

  useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: { style: 'overflow: hidden; background-color: #212121; background-repeat: no-repeat; background-size: cover;' }
})
  const api = useApi()
  const route = useRoute()

  const loading = ref(true)

  const plushdata = ref()
  const postdata = ref()
  const sharkeydata = ref()
  const plusherror = ref()
  const postserror = ref()
  const friendsdata = ref()

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
    friendsdata.value = hajData?.friends
    plusherror.value = err
    postserror.value = err2
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
      <h2>Friends</h2>
      <div class="friend-list">
        <a :href="`/plush/${friend.uuid}`" class="friend" v-for="friend in friendsdata">
          <div class="small-friend-pfp" :style="{ backgroundImage: `url(/api/hajs/${friend.uuid}/pfp)` }"></div>
          <span class="small-friend-name">{{friend.displayname}}</span>
        </a>
      </div>
    </div>
    <div class="stat">
      <h2>Badges</h2>
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
  <div class="tile" :style="{ backgroundImage: `url(/api/hajs/${route.params.id}/pfp)` }"></div>
  <div class="tile"></div>
  <div class="tile stat">
    <h2>Size</h2>
    <h1 style="background-image: radial-gradient(circle at top left, #FF9A41 0, #995C27 100%);">{{plushdata.size}}<span style="font-size: 2rem;">cm</span></h1>
  </div>
  <div class="tile stat">
    <h2>Gender</h2>
    <h3>{{plushdata.gender}}</h3>
  </div>
  <div class="tile stat-pair">
    <span>Fluffiness</span>
    <div v-if="plushdata.floof != null" class="pair-row">
      <div class="pair-bar">
        <div class="pair-fill" :style="{ width: (plushdata.floof / 10 * 100) + '%' }"></div>
      </div>
      <span>{{plushdata.floof}}/10</span>
    </div>
    <span>Squish</span>
    <div v-if="plushdata.squish != null" class="pair-row">
      <div class="pair-bar">
        <div class="pair-fill" :style="{ width: (plushdata.squish / 10 * 100) + '%' }"></div>
      </div>
      <span>{{plushdata.squish}}/10</span>
    </div>
  </div>
  <div class="tile stat-pair">
    <span>Adopted on:</span>
    <span>{{plushdata.date}}</span>
    <span v-if="plushdata.lastwashed != null">Last washed:</span>
    <span v-if="plushdata.lastwashed != null">{{timeAgo(plushdata.lastwashed)}}</span>
  </div>
  <div class="tile stat" v-if="plushdata.mloftearsabsorbed != null">
    <h2>tears absorbed:</h2>
    <h1 style="background-image: radial-gradient(circle at top left, #418DFF 0, #275599 100%);">{{plushdata.mloftearsabsorbed}}<span style="font-size: 2rem;">mL</span></h1>
  </div>
</div>
</template>

<style scoped>
.friend-list {
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  height: 100%;
  width: 100%;
  padding: 0.2rem;
  padding-top: 3rem;
  gap: 0.8rem;
  overflow-y: scroll;
}

.friend {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 2.2rem;
  padding: 0.3rem;
  background-color: #FFBD52A0;
  outline: 0.15rem solid #FFBD52;
  border-radius: 9px;
  gap: 0.5em;
  color: #E3E3E3;
  text-decoration: none;
}

.small-friend-name {
  font-size: 1.3rem;
}

.small-friend-pfp {
  box-sizing: border-box;
  background-size: cover;
  background-position: center;
  height: 100%;
  aspect-ratio: 1/1;
  border-radius: 7px;
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
  overflow: hidden;
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

.tile:nth-child(10) h1 {
  font-size: 3rem;
}

.stat-pair {
  display: grid;
  flex-direction: column;
  padding: 1em 1.3em;
  gap: 0.6em;
  font-size: 1.1em;
  font-weight: 500;
}

.pair-row {
  display: flex;
  align-items: center;
  gap: 0.5em;
}

.pair-bar {
  flex: 1;
  height: 1.2em;
  border-radius: 0.35em;
  background-color: #4A4A4A;
  overflow: hidden;
}

.pair-fill {
  height: 100%;
  border-radius: 0.35em;
  background: linear-gradient(90deg, #B088D6, #8B5CF6);
  transition: width 0.3s;
}
</style>
