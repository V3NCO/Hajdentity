<script setup lang="ts">
import { useApi } from '~/lib/api'

useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: { style: 'overflow: hidden; background-color: #212121; background-repeat: no-repeat; background-size: cover;' }
})
const auth = useAuth()
const api = useApi()
const state = reactive({
  email: undefined,
  password: undefined
})

const user = auth.user

definePageMeta({ middleware: 'auth', ssr: false })



async function onEmailSubmit() {
  try {
    await $fetch("/api/auth/email", { method: 'PUT', body: { email: state.email }, credentials: 'include' })
    alert('Email changed!')
  } catch (e) {
    alert((e as any)?.response?._data?.detail || (e as any)?.data?.detail || 'Registration failed')
  }
}

async function onPasswordSubmit() {
  try {
    await $fetch("/api/auth/password", { method: 'PUT', body: { password: state.password }, credentials: 'include' })
    alert('Password changed!')
  } catch (e) {
    alert((e as any)?.response?._data?.detail || (e as any)?.data?.detail || 'Registration failed')
  }
}

async function onDelete() {
  try {
    await $fetch("/api/auth/delete", { method: 'DELETE', credentials: 'include' })
    alert('Account deleted. Your session is now invalid, you can refresh.')
  } catch (e) {
    alert((e as any)?.response?._data?.detail || (e as any)?.data?.detail || 'Deletion... Failed? Contact the administrator')
  }
}
</script>


<template>
<div class="leftcont">
  <div class="sidebar">
    <a href="#"><Icon class="beeg" name="material-symbols:account-circle"/></a>
    <hr/>
    <a href="plushies"><Icon class="beeg" name="hajdentity:haj"/></a>
  </div>
</div>
<div class="rightcont">
  <div class="dash">
    <form name="email-change" @submit.prevent="onEmailSubmit">
      <div class="field" v-if="user">
        <label for="note">Email</label>
        <input
          name="email"
          v-model="state.email"
          type="email"
          :placeholder="user?.email"
          required
        />
        <button type="submit"><h3>Submit</h3></button>
      </div>
    </form>

    <form name="password-change" @submit.prevent="onPasswordSubmit">
      <div class="field" v-if="user">
        <label for="note">Password</label>
        <input
          name="passoword"
          v-model="state.password"
          type="password"
          minlength=16
          required
        />
        <button type="submit"><h3>Submit</h3></button>
      </div>
    </form>

    <div class="danger-zone">
      <span>WARNING: This will INSTANTLY delete your account, no warning, no nothing. All of your data will be gone and unrecoverable.</span>
      <button @click="onDelete"><h3>Delete account</h3></button>
    </div>

    <p style="color: #E3E3E3;">For anything else please contact the admin, this dashboard is rushed honestly and needs improving with auth as whole</p>
  </div>
</div>
</template>

<style scoped>
.danger-zone {
  width: 100%;
  height: fit-content;
  background-color: #EE4444A0;
  padding: 3rem;
  box-sizing: border-box;
  border-radius: 18px;
  outline: 5px dashed #FF2222;
}

.danger-zone span {
  font-size: 1.2rem;
  font-weight: 700;
}
.danger-zone button {
  color: black;
  width: 10rem;
}

.dash {
  background-color: #2D2D2D;
  box-sizing: border-box;
  height: 100%;
  border-radius: 18px;
  display: grid;
  padding: 1.5em;
}

.leftcont {
  float: left;
  height: 100svh;
  padding: 1rem;
  box-sizing: border-box;
}

.rightcont {
  height: 100svh;
  width: 100%;
  padding: 1rem;
  box-sizing: border-box;
}

.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
  width: 4rem;
  padding: 0.75rem;
  background-color:#2D2D2D;
  border-radius: 18px;
  gap: 0.75rem;
}

.sidebar a {
  width: 100%;
  aspect-ratio: 1/1;
  box-sizing: border-box;
  color: #E3E3E3;
  text-decoration: none;
}

.sidebar hr {
  margin: 0;
  box-sizing: border-box;
}

.beeg {
  height: 100%;
  width: 100%;
}

.midcont {
  display: flex;
  flex-direction: column;
  font-family:  "Space Grotesk";
  height:100svh;
  width: 100vw;
  max-width: 50rem;
  box-sizing: border-box;
  gap: 3em;
  padding: 2em;
  margin: 0 auto;
}

.act-topline {
  display: flex;
  flex-direction: row;
  height: 17.5svh;
  max-height: 17.5svh;
  gap: 2rem;
  font-weight: 500;
}

.act-topline h1 {
  font-size: 2.5rem;
  color: #E3E3E3;
  gap: 1rem;
  margin: 0;
}

.act-topline p {
  font-size: 1rem;
  color: #E3E3E3;
  margin: 0;
  font-weight: 400;
}

.act-pronouns {
  font-family: "Montserrat";
  font-weight: 400;
  font-size: 1.5rem;
}

.act-title {
  display:flex;
  flex-direction:column;
  overflow: hidden;
}

.act-username {
  font-family: "Space Grotesk";
  font-weight: 300;
  color: #E3E3E3;
  font-size: 1.5rem;
  margin-top: 0;
}

.act-pfp {
  outline: 0.4em solid #638FAC;
  aspect-ratio: 1 / 1;
  background-size: cover;
  background-position: center;
  border-radius: 35px;
}

input {
  resize: none;
  box-sizing: border-box;
  width: 30rem;
  border-radius: 12px;
  background-color: #2D2D2D;
  outline: 0.15rem solid #404040;
  padding:0.7rem;
  border: none;
  color: #E3E3E3;
  font-size: 1rem;
  margin-top: 1.3rem;
  height: 3rem;
}

button {
  display: grid;
  justify-content: center;
  align-items: center;
  border: none;
  border-radius: 10px;
  background-color: #E3E3E3;
  box-sizing: border-box;
  color: #E3E3E3;
  text-align: center;
  gap: 0.2em;
  margin-top: 1.3rem;
  height: 3rem;
  width: 7rem;
}

.field {
  position: relative;
  display: flex;
  gap: 1rem;
}

.field label {
  position: absolute;
  left: 0.5rem;
  top: 0.5rem;
  transform: translateY(-50%);
  font-size: 0.9rem;
  font-weight: 500;
  color: #636363;
}

.field button h3 {
  margin: 0;
  color: #2D2D2D;
}
</style>
