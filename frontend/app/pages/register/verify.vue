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
  const { data, error } = await useFetch<{ status: string; email: string }>('/api/auth/verify', {
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
  try {
    await $fetch("/api/auth/new_verification_token", { method: 'POST', body: { email: email.value } })
    alert("An email has been sent if the email is registered and unverified. Please check your inbox and spam.")
  } catch (e) {
    alert((e as any)?.response?._data?.detail || (e as any)?.data?.detail || 'Failed to resend verification email')
  }
}

useSeoMeta({
  title: 'Verify',
  description: 'Verify your email address!',
})

useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: {
    style: 'overflow: hidden; background-image: url("/stocksharks.jpeg"); background-repeat: no-repeat; background-size: cover; font-family: "Noto Sans";'
  }
})
</script>

<template>
<div class="auth-page">
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
</div>
</template>

<style scoped>
.auth-page input { border-radius: 10rem; border: 2px solid #95ADB6; background-color: #C3D0D5; font-weight: 600; color: black; }
.auth-page button { border-radius: 1rem; border: 2px solid #95ADB6; background-color: #C3D0D5; font-weight: 700; }
.auth-page button:hover { border: 3px solid #95ADB6; background-color: #E3F0F5; }
.auth-page button:active { border: 3px solid #859DA6; background-color: #A3B0B5; }
.auth-page input:user-invalid { border: 2px solid #EF959C; background-color: #F7CACE; }
.auth-page .err { color: #EC839B; background-color: #F7CACE; font-size: 0.85rem; font-weight: 600; margin: -0.5rem 0 0 0; text-align: left; align-self:auto; padding: 0.25rem 0.75rem 0.25rem 0.75rem; border-radius: 3em; display: inline-flex; align-items: center; gap: 0.15rem; }
.auth-page .rcont, .auth-page .vcont { box-sizing: border-box; }
.auth-page .rcont { width: 50vw; height: 100svh; position: relative; float: right; padding: 1em; overflow: hidden; }
.auth-page .vcont { padding: 1em; height: 100%; background-image: linear-gradient(147deg, #9FB2CACC, #5D7798CC); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 18px; border: 1px solid rgba(255,255,255,0.3); display: flex; justify-content: center; align-items: center; text-align: center; }
.auth-page form { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; height: 100%; }
.auth-page form input { width: 80%; height: 4%; padding: 0.25rem 0.25rem 0.25rem 2rem; }
.auth-page form button { margin-top: 1em; width: 80%; height: 2.5rem; }
.auth-page h1 { margin: 1rem; }
.auth-page .bigicon { font-size: 20vmin; }
.auth-page a { border-radius: 10rem; border: 2px solid #95ADB6; background-color: #C3D0D5; font-weight: 600; padding: 0.5rem 1rem; }
@media screen and (max-width: 790px) { .rcont { width: 100vw } }
</style>
