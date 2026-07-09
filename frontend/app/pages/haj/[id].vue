<script setup lang="ts">
  import '~/assets/css/fonts.css'

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

  const displayName = "Raine";
  const username = "raine";
  const pronouns = "they/them";
  const location = "France";
  const description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin imperdiet ultricies risus vitae pellentesque. Morbi porta, nisl nec viverra  aliquet, eros mauris rutrum magna,";
  const likes = 13292;
  const views = 4343333;
  const posts = 1;
  const followers = 132;
</script>

<template>
<div class="bento">
  <div class="tile">
    <h1 class="topline">{{displayName}} <span class="pronouns">{{pronouns}}</span> <span class="location">📍 {{location}}</span></h1>
    <h2 class="username">@{{username}}</h2>
    <p>{{description}}</p>
  </div>
  <div class="tile"></div>
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
      <h1 style="background-image: radial-gradient(circle at top left, #0D76FF 0, #084799 100%);">{{formatCompactNumber(posts)}}</h1>
    </div>
    <div class="stat">
      <h2>Followers</h2>
      <h1 style="background-image: radial-gradient(circle at top left, #AD41FF 0, #682799 100%);">{{formatCompactNumber(followers)}}</h1>
    </div>
  </div>
  <div class="tile"></div>
  <div class="tile"></div>
  <div class="tile"></div>
  <div class="tile"></div>
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
}

.tile:nth-child(3) {
  grid-column:  1 / 4;
  grid-row: 3 / 6;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  background-color: #212121;
  padding: 0;
  gap: 1em
}

/* PFP in middle */
.tile:nth-child(4) {
  grid-column:  4;
  grid-row: 3;
  outline: 0.4em solid #638FAC;
}

.tile:nth-child(5) {
  grid-column:  4;
  grid-row: 4 / 6;
}

.tile:nth-child(6) {
  grid-column:  5;
  grid-row: 4;
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
