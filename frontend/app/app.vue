<template>
  <div>
    <NuxtPage />
  </div>
</template>
<style>
html, body {
  height: 100%;
  margin: 0;
}

body {
  overflow: hidden;
  background-image: url("/stocksharks.jpeg");
  font-family: "Noto Sans";
  /* Eventually this would be an animated carousel of shark images from users */
  /* Maybe scrolling cards, because simple images side by side would look wrong and blending them with gradients would look wrong too */
}

#app, #__nuxt {
  height: 100%;
}


input {
  border-radius: 10rem;
  border: 2px solid #95ADB6;
  background-color: #C3D0D5;
  font-weight: 600;
  color: black;
}

button {
  border-radius: 1rem;
  border: 2px solid #95ADB6;
  background-color: #C3D0D5;
  font-weight: 700;
}

button:hover {
  border: 3px solid #95ADB6;
  background-color: #E3F0F5;
}

button:active {
  border: 3px solid #859DA6;
  background-color: #A3B0B5;
}

input:user-invalid {
  border: 2px solid #EF959C;
  background-color: #F7CACE;
}

.err {
  color: #EC839B;
  background-color: #F7CACE;
  font-size: 0.85rem;
  font-weight: 600;
  margin: -0.5rem 0 0 0;
  text-align: left;
  align-self:auto;
  padding: 0.25rem 0.75rem 0.25rem 0.75rem;
  border-radius: 3em;
  display: inline-flex;
  align-items: center;
  gap: 0.15rem;
}
</style>
