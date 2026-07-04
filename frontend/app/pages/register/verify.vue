<script setup lang="ts">
import { ref } from 'vue'

const route = useRoute()
const { token, sent } = route.query
const email = ref('')
const isSent = ref(false)
const isExpired = ref(false)
const isInvalid = ref(false)
const isVerified = ref(false)

if (token) {
  const { data, error } = await useFetch('/api/auth/verify', {
    method: 'POST',
    body: {
      token: token,
    }
  })
  console.log(data.value)

  console.log(error.value?.status)

  if (error.value) {
    if (error.value?.status === 403) { isExpired.value = true; }
    else if (error.value?.status === 400) { isInvalid.value = true }
  } else {
    isVerified.value = true;
    email.value = data.value?.email ?? ''
  }
}

if (sent) {
  isSent.value = true
}


async function onSubmit() {
  await $fetch("/api/auth/new_verification_token", { method: 'POST', body: { email: email.value } })
  alert("An email has been sent if the email is registered and unverified. Please check your inbox and spam.")
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
    <div v-else-if="isExpired">
      <h1>This token is Expired!</h1>
      <Icon class="bigicon" name="material-symbols:hourglass-disabled"/>
      <p>You have opened the link too late, please try resending an email with the link below!</p>
      <a href="/register/verify">Resend an email</a>
    </div>
    <div v-else-if="isVerified">
      <h1>Email Verified!</h1>
      <Icon class="bigicon" name="material-symbols:verified-outline"/>
      <p>Your email {{ email }} is verified, you can now login to your account!</p>
      <a href="/login">Login</a>
    </div>
    <div v-else-if="isInvalid">
      <h1>This token is Invalid!</h1>
      <Icon class="bigicon" name="material-symbols:error-outline"/>
      <p>The token entered could not be verified, please try resending an email with the link below!</p>
      <a href="/register/verify">Resend an email</a>
    </div>
    <form v-else ref="ResendVerifEmailForm" @submit.prevent="onSubmit" >
      <h1>Resend a verification email</h1>
      <input
        v-model="email"
        id="email"
        name="email"
        type="email"
        placeholder="Email address"
        required
      />
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

a {
  border-radius: 10rem;
  border: 2px solid #95ADB6;
  background-color: #C3D0D5;
  font-weight: 600;
  padding: 0.5rem 1rem;
}

form {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  height: 100%;
  width: 100%;
}
</style>
