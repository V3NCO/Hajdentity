<script setup lang="ts">
import { useApi } from '~/lib/api'

useHead({ htmlAttrs: { lang: 'en' }})
const api = useApi()
const route = useRoute()

const newMode = ref(false)
const useMode = ref(false)
const code = ref("")
const newCodeDigits = ref(["", "", "", "", "", "", "", ""])
const digitInputs = ref<(HTMLInputElement | undefined)[]>([])

function onInput(e: Event, i: number) {
  const val = (e.target as HTMLInputElement).value
  newCodeDigits.value[i] = val.replace(/\D/g, "").slice(0, 1)
  if (newCodeDigits.value[i] && i < 7) {
    digitInputs.value[i + 1]?.focus()
  }
}

function onDel(e: Event, i: number) {
  if (!newCodeDigits.value[i] && i > 0) {
    digitInputs.value[i - 1]?.focus()
  }
}

function setRef(el: any, i: number) {
  if (el) digitInputs.value[i] = el as HTMLInputElement
}

async function newCode() {
  code.value = "Loading.";
  newMode.value = true;
  const { data: hajData, error: err } = await api.GET(
    '/api/hajs/{haj_id}',
    { params: { path: { haj_id: route.params.id as string } } }
  )
}

async function useCode() {
  useMode.value = true;
}

</script>
<template>
<div class="friend-topline">
  <div class="friend-title">
     <h1><Icon name="material-symbols:person-add-outline"/> Add Friend</h1>
     <h2 class="friend-explaination">Make a code, tap your friend and use the code to become friends!</h2>
  </div>
</div>
<Transition><div class="friend-pfp" :class="{ 'new-mode': newMode, 'use-mode': useMode }" :style="{ backgroundImage: `url(/api/hajs/${route.params.id}/pfp)` }"></div></Transition>
<Transition><div v-if="useMode" class="friend-code">
  <div class="code-inputs">
    <input
      v-for="(digit, i) in newCodeDigits.slice(0, 4)"
      :key="i"
      type="text"
      inputmode="numeric"
      maxlength="1"
      pattern="\d"
      v-model="newCodeDigits[i]"
      @input="onInput($event, i)"
      @keydown.backspace="onDel($event, i)"
      :ref="(el: any) => setRef(el, i)"
      class="code-digit"
    />
    <span class="code-dash">—</span>
    <input
      v-for="(digit, i) in newCodeDigits.slice(4)"
      :key="i + 4"
      type="text"
      inputmode="numeric"
      maxlength="1"
      pattern="\d"
      v-model="newCodeDigits[i + 4]"
      @input="onInput($event, i + 4)"
      @keydown.backspace="onDel($event, i + 4)"
      :ref="(el: any) => setRef(el, i + 4)"
      class="code-digit"
    />
  </div>
  <h1>Input Code</h1>
</div></Transition>

<div v-if="newMode" class="friend-code">
  <span>{{code}}</span>
  <h1>Friend Code</h1>
</div>
<div class="midbotcont" :class="{ 'new-mode': newMode, 'use-mode': useMode }">
  <button class="button" @click="newCode"><h1><Icon name="material-symbols:add" :class="{ 'new-mode': newMode, 'use-mode': useMode }"/>New Code</h1></button>
  <button class="button" @click="useCode"><h1><Icon name="material-symbols:password" :class="{ 'new-mode': newMode, 'use-mode': useMode }"/> Use Code</h1></button>
</div>
</template>

<style>
html, body {
  height: 100%;
  margin: 0;
}

body {
  overflow: hidden;
  background-color: #212121;
  background-repeat: no-repeat;
  background-size: cover;
}

#app, #__nuxt {
  height: 100%;
  display: flex;
  justify-content: center;
}

.midbotcont {
  position: fixed;
  bottom: 0rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: row;
  font-family:  "Space Grotesk";
  height:10svh;
  width: 100vw;
  max-width: 40rem;
  box-sizing: border-box;
  gap: 1.5em;
  padding: 1em;
  transition: transform 0.5s ease-out;
}

.midbotcont.new-mode,
.midbotcont.use-mode {
  transform: translate(-50%, 100%);
}

.friend-topline {
  display: flex;
  flex-direction: column;
  font-weight: 500;
  position: absolute;
  top: 0;
  left: 0;
}

.friend-topline h1 {
  display: flex;
  font-size: 2.5rem;
  font-family: "Space Grotesk";
  font-weight: 500;
  color: #E3E3E3;
  gap: 0.75rem;
  margin: 0;
  padding: 1rem;
  padding-bottom: 0.25rem;
  align-items: center;
}

.friend-topline h2 {
  font-size: 1.25rem;
  font-family: "Oswald";
  font-weight: 400;
  color: #636363;
  margin: 0;
  padding-left: 1rem;
  align-items: center;
}

.friend-pfp {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  outline: 0.4em solid #638FAC;
  aspect-ratio: 1 / 1;
  background-size: cover;
  background-position: center;
  border-radius: 35px;
  width: 10rem;
  height: 10rem;
  filter: drop-shadow(0 0 5rem #638FAC);
  transition: all 0.5s ease-out;
}

.friend-pfp.new-mode,
.friend-pfp.use-mode {
  transform: translate(-50%, -180%);
}

.friend-code {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.friend-code h1 {
  margin: 0;
  font-family: "Space Grotesk";
  font-size: 2rem;
  font-weight: 500;
  color: #E3E3E3;
  pointer-events: none;
}

.code-inputs {
  display: flex;
  flex-direction: row;
  gap: 0.75rem;
  justify-content: center;
}

.code-digit {
  width: 2.5rem;
  height: 3.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid #E3E3E3;
  color: #E3E3E3;
  font-family: "Space Grotesk";
  font-size: 2rem;
  text-align: center;
  outline: none;
  transition: border-color 0.2s;
}

.code-digit:focus {
  border-bottom-color: #638FAC;
}

.code-dash {
  color: #E3E3E3;
  font-family: "Space Grotesk";
  font-size: 2rem;
}

.button {
  flex-grow:1;
  display: grid;
  justify-content: center;
  align-items: center;
  border: none;
  border-radius: 10px;
  background-color: #2D2D2D;
  outline: 0.15rem solid #404040;
  box-sizing: border-box;
  color: #E3E3E3;
  text-align: center;
  gap: 0.2em;
}

.button h1 {
  display: flex;
  font-size: 1.5rem;
  font-family: "Space Grotesk";
  font-weight: 500;
  color: #E3E3E3;
  gap: 0.75rem;
  margin: 0;
  align-items: center;
}


.v-enter-active,
.v-leave-active {
  transition: opacity 0.8s ease-in;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}

@media screen and (max-width: 500px) {

}
</style>
