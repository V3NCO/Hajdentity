<script setup lang="ts">
useSeoMeta({
  title: 'Login',
  description: 'Login to your account on Hajdentity!',
  ogTitle: 'Login',
  ogDescription: 'Login to your account on Hajdentity!',
  ogImage: '[og:image]',
  ogUrl: 'https://id.blahaj.engineering/login',
  twitterTitle: 'Login',
  twitterDescription: 'Login to your account on Hajdentity!',
  twitterImage: '[twitter:image]',
  twitterCard: 'summary'
})

definePageMeta({ middleware: 'guest' })
useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: {
    style: 'overflow: hidden; background-image: url("/stocksharks.jpeg"); background-repeat: no-repeat; background-size: cover; font-family: "Noto Sans";'
  }
})
const route = useRoute()
const auth = useAuth()

const username = ref('')
const password = ref('')

type FieldErrors = Partial<Record<'username' | 'password', string>>
const errors = ref<FieldErrors>({})
const serverError = ref('')
const submitting = ref(false)

function validate(field: 'all' | 'username' | 'password') {
  const next: FieldErrors = { ...errors.value }

  if (field === "all" || field === "username") {
    delete next.username
    if (!username.value) next.username = 'Username is required'
  }

  if (field === "all" || field === "password") {
    delete next.password
    if (!password.value) next.password = 'Password is required'
  }

  errors.value = next
  return Object.keys(next).length === 0
}

function onInput(field: 'username' | 'password') {
  validate(field)
}

async function onSubmit() {
  serverError.value = ''
  if (!validate('all')) return

  submitting.value = true
  try {
    await auth.login(username.value, password.value)
    const redirect = (route.query.redirect as string) || '/'
    await navigateTo(redirect)
  } catch (e: any) {
    serverError.value = e?.data?.detail || 'Login failed. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
<div class="rcont">
  <div class="vcont">
    <form @submit.prevent="onSubmit" novalidate>
      <h1>Login</h1>
      <input v-model="username" @input="onInput('username')" id="username" name="username" placeholder="Your Human name :3" type="text" autocomplete="username" required />
      <p v-if="errors.username" class="err"><Icon name="material-symbols:error" style="justify-self: center;"/> {{ errors.username }}</p>
      <input v-model="password" @input="onInput('password')" id="password" name="password" type="password" placeholder="Veri secure password" autocomplete="current-password" required />
      <p v-if="errors.password" class="err"><Icon name="material-symbols:error" /> {{ errors.password }}</p>
      <p v-if="serverError" class="err"><Icon name="material-symbols:error" /> {{ serverError }}</p>
      <button type="submit" :disabled="submitting">{{ submitting ? 'Logging in...' : 'Submit' }}</button>
      <p>Don't have an account yet? <NuxtLink to="/register">Register here</NuxtLink></p>
    </form>
  </div>
</div>
</template>

<style scoped>
input { border-radius: 10rem; border: 2px solid #95ADB6; background-color: #C3D0D5; font-weight: 600; color: black; }
button { border-radius: 1rem; border: 2px solid #95ADB6; background-color: #C3D0D5; font-weight: 700; }
button:hover { border: 3px solid #95ADB6; background-color: #E3F0F5; }
button:active { border: 3px solid #859DA6; background-color: #A3B0B5; }
input:user-invalid { border: 2px solid #EF959C; background-color: #F7CACE; }
.err { color: #EC839B; background-color: #F7CACE; font-size: 0.85rem; font-weight: 600; margin: -0.5rem 0 0 0; text-align: left; align-self:auto; padding: 0.25rem 0.75rem 0.25rem 0.75rem; border-radius: 3em; display: inline-flex; align-items: center; gap: 0.15rem; }
.rcont, .vcont { box-sizing: border-box; }
.rcont { width: 50vw; height: 100svh; position: relative; float: right; padding: 1em; overflow: hidden; }
.vcont { padding: 1em; height: 100%; background-image: linear-gradient(147deg, #9FB2CACC, #5D7798CC); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 18px; border: 1px solid rgba(255,255,255,0.3); }
form { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; height: 100%; }
form input { width: 80%; height: 4%; padding: 0.25rem 0.25rem 0.25rem 2rem; }
form button { margin-top: 1em; width: 80%; height: 2.5rem; }
p { margin: 0; }
@media screen and (max-width: 790px) { .rcont { width: 100vw } }
</style>