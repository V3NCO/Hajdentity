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

useHead({ htmlAttrs: { lang: 'en' } })
import '~/assets/css/auth.css'

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
      <input
        v-model="username"
        @input="onInput('username')"
        id="username"
        name="username"
        placeholder="Your Human name :3"
        type="text"
        autocomplete="username"
        required
      />
      <p v-if="errors.username" class="err">
        <Icon name="material-symbols:error" style="justify-self: center;"/>
        {{ errors.username }}
      </p>
      <input
        v-model="password"
        @input="onInput('password')"
        id="password"
        name="password"
        type="password"
        placeholder="Veri secure password"
        autocomplete="current-password"
        required
      />
      <p v-if="errors.password" class="err">
        <Icon name="material-symbols:error" />
        {{ errors.password }}
      </p>
      <p v-if="serverError" class="err">
        <Icon name="material-symbols:error" />
        {{ serverError }}
      </p>
      <button type="submit" :disabled="submitting">
        {{ submitting ? 'Logging in...' : 'Submit' }}
      </button>
      <p>
        Don't have an account yet? <NuxtLink to="/register">Register here</NuxtLink>
      </p>
    </form>
  </div>
</div>
</template>

<style scoped>
p {
  margin: 0;
}
</style>
