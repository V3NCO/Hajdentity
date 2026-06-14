<script setup lang="ts">
import { ref } from 'vue'

const route = useRoute()
const { token, sent } = route.query
const hasToken = ref(false)
const isSent = ref(false)

if (token) {
  hasToken.value = true
  const { data, error } = await useFetch('/api/auth/verify', {
    method: 'POST',
    body: {
      token: token,
    }
  })

}

if (sent) {
  isSent.value = true
}

useSeoMeta({
  title: 'Verify',
  description: 'Verify your email address!',
})

useHead({ htmlAttrs: { lang: 'en' } })
</script>

<template>
<div class="rcont">
  <div class="vcont">
    <div v-if="isSent">
      <h1>Verify your Email</h1>
      <Icon class="bigicon" name="material-symbols:mark-email-unread-outline"/>
      <p>We've sent a mail to your inbox, if you don't see it; make sure to check your spam folder.</p>
      <a href="/register/verify">Resend an email</a>
    </div>
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
  background-image: url("/stocksharks.jpeg");
  font-family: "Arial";
  /* Eventually this would be an animated carousel of shark images from users */
  /* Maybe scrolling cards, because simple images side by side would look wrong and blending them with gradients would look wrong too */
}

#app, #__nuxt {
  height: 100%;
}

.rcont, .vcont {
  box-sizing: border-box;
}

.rcont {
  width: 50vw;
  height: 100svh;
  position: relative;
  float: right;
  padding: 1em;
  overflow: hidden;
}

.vcont {
    display: flex;
    padding: 1em;
    height: 100%;
    width: 100%;
    background-image: linear-gradient(147deg, #9FB2CACC, #5D7798CC);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    justify-content: center;
    align-items: center;
    text-align: center;
}

input {
  width: 80%;
  height: 4%;
  border-radius: 10rem;
  padding: 0.25rem 0.25rem 0.25rem 2rem
}

button {
  margin-top: 1em;
  width: 80%;
  height: 2.5rem;
}

h1 {
    margin: 1rem;
}
.bigicon {
    font-size: 20vmin;
}
</style>
