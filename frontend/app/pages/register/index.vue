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

definePageMeta({ middleware: 'guest' })
useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: {
    style: 'overflow: hidden; background-image: url("/stocksharks.jpeg"); background-repeat: no-repeat; background-size: cover; font-family: "Noto Sans";'
  }
})

const registerForm = ref<HTMLFormElement | null>(null)
const username = ref('')
const email = ref('')
const password = ref('')

type FieldErrors = Partial<Record<'username' | 'email' | 'password', string>>
const errors = ref<FieldErrors>({})

function validate(field: 'all' | 'username' | 'email' | 'password') {
  const next: FieldErrors = { ...errors.value }

  if (field === "all" || field === "username") {
    delete next.username
    const u = username.value
    if (!u) next.username = 'Username is required'
    else if (u.length < 3) next.username = 'Username must be at least 3 characters'
    else if (u.length > 96) next.username = 'Username must be at most 96 characters'
    else if (!/^(?:[A-Za-z0-9_]|-){3,96}$/.test(u)) next.username = 'Only letters, numbers, underscores, and hyphens allowed'
  }

  if (field === "all" || field === "email") {
    delete next.email
    const e = email.value
    if (!e) next.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)) next.email = 'Enter a valid email address'
  }

  if (field === "all" || field === "password") {
    delete next.password
    const p = password.value
    if (!p) next.password = 'Password is required'
    else if (p.length < 16) next.password = 'Password must be at least 16 characters'
  }

  errors.value = next
  return Object.keys(next).length === 0
}

function onInput(field: 'username' | 'email' | 'password') {
  validate(field)
}

async function onSubmit() {
  if (!validate('all')) return

  try {
    await $fetch("/api/auth/register", { method: 'POST', body: { username: username.value, email: email.value, password: password.value } })
    await navigateTo('/register/verify?sent=true')
  } catch (e) {
    alert((e as any)?.response?._data?.detail || (e as any)?.data?.detail || 'Registration failed')
  }
}
</script>

<template>
<div class="auth-page">
<div class="rcont">
  <div class="vcont">
    <form ref="registerForm" @submit.prevent="onSubmit" novalidate>
      <h1>Register</h1>
      <input
        v-model="username"
        @input="onInput('username')"
        id="username"
        name="username"
        placeholder="Your Human name :3"
        type="text"
        minlength=3
        maxlength=96
        pattern="(?:[A-Za-z0-9_]|-){3,96}"
        required
      />
      <p v-if="errors.username" class="err">
        <Icon name="material-symbols:error" style="justify-self: center;"/>
        {{ errors.username }}
      </p>
      <input
        v-model="email"
        @input="onInput('email')"
        id="email"
        name="email"
        type="email"
        placeholder="Email address!"
        required
      />
      <p v-if="errors.email" class="err">
        <Icon name="material-symbols:error" />
        {{ errors.email }}
      </p>
      <input
        v-model="password"
        @input="onInput('password')"
        id="password"
        name="password"
        type="password"
        placeholder="Veri secure password"
        minlength=16
        required
      />
      <p v-if="errors.password" class="err">
        <Icon name="material-symbols:error" />
        {{ errors.password }}
      </p>
      <button type="submit">Submit</button>
    </form>
  </div>
</div>
</div>
</template>

<style>
html, body { height: 100%; margin: 0; }
#app, #__nuxt { height: 100%; }
.auth-page { height: 100%; }
.auth-page input { border-radius: 10rem; border: 2px solid #95ADB6; background-color: #C3D0D5; font-weight: 600; color: black; }
.auth-page button { border-radius: 1rem; border: 2px solid #95ADB6; background-color: #C3D0D5; font-weight: 700; }
.auth-page button:hover { border: 3px solid #95ADB6; background-color: #E3F0F5; }
.auth-page button:active { border: 3px solid #859DA6; background-color: #A3B0B5; }
.auth-page input:user-invalid { border: 2px solid #EF959C; background-color: #F7CACE; }
.auth-page .err { color: #EC839B; background-color: #F7CACE; font-size: 0.85rem; font-weight: 600; margin: -0.5rem 0 0 0; text-align: left; align-self:auto; padding: 0.25rem 0.75rem 0.25rem 0.75rem; border-radius: 3em; display: inline-flex; align-items: center; gap: 0.15rem; }
.auth-page .rcont, .auth-page .vcont { box-sizing: border-box; }
.auth-page .rcont { width: 50vw; height: 100svh; position: relative; float: right; padding: 1em; overflow: hidden; }
.auth-page .vcont { padding: 1em; height: 100%; background-image: linear-gradient(147deg, #9FB2CACC, #5D7798CC); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-radius: 18px; border: 1px solid rgba(255,255,255,0.3); }
.auth-page form { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; height: 100%; }
.auth-page form input { width: 80%; height: 4%; padding: 0.25rem 0.25rem 0.25rem 2rem; }
.auth-page form button { margin-top: 1em; width: 80%; height: 2.5rem; }
</style>

<style scoped>
@media screen and (max-width: 790px) {
	.rcont {
	  width: 100vw
	}
}
</style>
