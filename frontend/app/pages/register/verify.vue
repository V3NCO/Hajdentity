<script setup lang="ts">
import { ref } from 'vue'
import authCss from '~/assets/css/auth.css?raw'
useHead({ style: [{ textContent: authCss }] })
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
.vcont {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
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
</style>
