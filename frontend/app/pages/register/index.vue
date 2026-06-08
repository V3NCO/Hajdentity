<script setup lang="ts">
useSeoMeta({
  title: 'Register',
  description: 'Make a new account on Hajdentity!',
  ogTitle: 'Register',
  ogDescription: 'Make a new account on Hajdentity!',
  ogImage: '[og:image]',
  ogUrl: 'https://id.blahaj.engineering/register',
  twitterTitle: 'Register',
  twitterDescription: 'Make a new account on Hajdentity!',
  twitterImage: '[twitter:image]',
  twitterCard: 'summary'
})

useHead({ htmlAttrs: { lang: 'en' } })

const registerForm = ref<HTMLFormElement | null>(null)
const username = ref('')
const email = ref('')
const password = ref('')

async function onSubmit() {
  const form = registerForm.value
  if (!form) return

  if (!form.checkValidity()) {
    form.reportValidity()
    return
  }

  await $fetch("/api/auth/register", { method: 'POST', body: { username: username.value, email: email.value, password: password.value } })
}

</script>

<template>
<div class="rcont">
  <div class="vcont">
    <form ref="registerForm" @submit.prevent="onSubmit">
      <input
        v-model="username"
        id="username"
        name="username"
        placeholder="Your Human name :3"
        type="text"
        minlength=3
        maxlength=96
        pattern="(?:[A-Za-z0-9_]|-){3,96}"
        required
      />
      <input v-model="email" id="email" name="email" type="email" placeholder="Email address!" required/>
      <input v-model="password" id="password" name="password" type="password" placeholder="Veri secure password" minlength=16 required/>
      <button type="submit">Submit</button>
    </form>
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
  /*Eventually this would be an animated carousel of shark images from users*/
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
    padding: 1em;
    height: 100%;
    width: 100%;
    background-image: linear-gradient(147deg, #F1CBBFCC, #F3A9BACC);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

form {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  height: 100%;
}

input {
  width: 80%;
  height: 1.75rem;
  border-radius: 10rem;
}

button {
  margin-top: 1em;
  width: 80%;
  height: 2.5rem;
  border-radius: 10rem;
}

input:user-invalid {
  box-shadow: 0 0 5px 1px red;
}
</style>
