<template>
<div class="bento">
  <div class="tile"></div>
  <div class="tile"></div>
  <div class="tile"></div>
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
  grid-row: span 1;
  border-radius: 35px;
  background-color: #2D2D2D;
  height: 100%;
  width: 100%;
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
