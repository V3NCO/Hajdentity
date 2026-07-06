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
import authCss from '~/assets/css/auth.css?raw'
useHead({ htmlAttrs: { lang: 'en' }, style: [{ textContent: authCss }] })

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

  await $fetch("/api/auth/register", { method: 'POST', body: { username: username.value, email: email.value, password: password.value } })
  await navigateTo('/register/verify?sent=true')
}

</script>

<template>
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
</template>

<style scoped>
@import url('~/assets/css/auth.css');
</style>
