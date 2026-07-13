<script setup lang="ts">
import { useApi } from '~/lib/api'

useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: { style: 'overflow: hidden; background-color: #404040; background-repeat: no-repeat; background-size: cover;' }
})

const api = useApi()
const route = useRoute()
const hajId = computed(() => route.query.haj as string)
const page = ref(0)
const tagId = ref('')
const provisionError = ref('')
const provisionned = ref()

async function next() {
  if (page.value <= 1) {
    page.value += 1
  } else if (page.value === 2) {
    if (!tagId.value.trim()) {
      provisionError.value = 'Tag ID is required'
      return
    }
    provisionError.value = ''
    const { data, error } = await api.POST('/api/nfc/provision', {
      body: { tag_id: tagId.value.trim(), haj_id: hajId.value }
    })
    if (error) {
      provisionError.value = typeof error === 'string' ? error : 'Provisioning failed'
      return
    }
    provisionned.value = data?.inserted
    page.value += 1
  } else if (page.value === 3) {
    page.value += 1
  } else {
    navigateTo(`/dashboard/plushies/${route.query.haj}`)
  }
}
</script>

<template>
<div class="card-hole" :class="page <= 2 ? 'hole-left' : 'hole-right'"></div>

<div class="lcont">
  <Transition><div class="center-content" v-if="page == 0">
      <Icon name="material-symbols:nfc"/><h1>Setup NFC</h1>
      <span>This will let you make people you meet IRL interact with your haj!</span>
  </div></Transition>
  <Transition><div class="center-content" v-if="page == 1">
      <Icon name="hajdentity:hajdentity-writer"/><h1>Install Hajdentity Writer</h1>
      <span>These NFC tags require specific commands to write to, this app will do everything for you, you can uninstall it after</span>
      <a download href="https://github.com/V3NCO/Hajdentity-Writer/releases/download/latest/app-release.apk">
        <h1>APK<Icon name="material-symbols:android"/></h1>
      </a>
      <a href="https://github.com/V3NCO/Hajdentity-Writer/releases/tag/latest">
        <h1>Github<Icon name="uil:github"/></h1>
      </a>
  </div></Transition>
  <Transition><div class="center-content" v-if="page == 2">
    <video autoplay loop muted playsinline><source src="~/assets/video/Overview.mp4" type="video/mp4"></video><h1>Input Code</h1>
      <span>Follow the above video and put the code wihout spaces</span>
      <input v-model="tagId" type="text" placeholder="Enter tag code" required minlength="14" maxlength="14" pattern="[0-9A-Fa-f]+" title="Hex characters only, no spaces" @keyup.enter="next"/>
  </div></Transition>
  <div class="nav-btns">
    <button class="next" @click="next"><h1>Next<Icon name="material-symbols:navigate-next"/></h1></button>
  </div>
</div>
<div class="rcont">
  <Transition><div class="center-content" v-if="page == 3">
    <Icon name="material-symbols:key-outline"/><h1>Store this somewhere safe</h1>
    <span>Here are your keys, please keep them somewhere safe, then write to the tag like the video that will be displayed</span>
  </div></Transition>
  <Transition><div class="center-content" v-if="page == 4">
    <video autoplay loop muted playsinline><source src="~/assets/video/Write.mp4" type="video/mp4"></video>
    <span class="key1"><span class="key2">Key0: </span>{{provisionned.key0}}</span>
    <span class="key1"><span class="key2">Key3: </span>{{provisionned.key3}}</span>
    <span class="key1"><span class="key2">Key4: </span>{{provisionned.key4}}</span>
  </div></Transition>
  <div class="nav-btns">
    <button class="next" @click="next"><h1>Next<Icon name="material-symbols:navigate-next"/></h1></button>
  </div>
</div>
</template>

<style scoped>
.card-hole {
  position: fixed;
  top: 1rem;
  width: calc(50vw - 2rem);
  height: calc(100svh - 2rem);
  border-radius: 24px;
  background: transparent;
  box-shadow: 0 0 0 200vw #212121;
  z-index: 100;
  pointer-events: none;
  transition: all 0.7s ease-out;
}

.hole-left {
  left: 1rem;
  right: auto;
  transform: translateX(0);
}

.hole-right {
  left: 1rem;
  right: auto;
  transform: translateX(50vw);
}

.key1 {
  font-family: "Montserrat" !important;
}

.key2 {
  font-family: "Montserrat" !important;
  font-weight: 600 !important;
  color: #E3E3E3 !important;
}

video {
  height: 25rem;
  justify-self: center;
}
.nav-btns {
  margin-top: auto;
  box-sizing: border-box;
  width: 100%;
  height: 3rem;
}

.nav-btns button:hover {
  outline: 0.15rem solid #636363;
  background-color: #404040;
}

.nav-btns button:active {
  outline: 0.15rem solid #636363;
  background-color: #636363;
}

.nav-btns button {
  display: grid;
  flex-direction: row;
  box-sizing: border-box;
  width: 25%;
  height: 3rem;
  justify-content: center;
  align-items: center;
  border: none;
  border-radius: 10px;
  background-color: #2D2D2D;
  outline: 0.15rem solid #404040;
  color: #E3E3E3;
  text-align: center;
  gap: 0.2em;
}

.nav-btns button h1 {
  display: flex;
  font-size: 1.5rem;
  font-family: "Space Grotesk";
  font-weight: 500;
  color: #E3E3E3;
  gap: 0.75rem;
  margin: 0;
  align-items: center;
}

.nav-btns .next {
  margin-left: auto;
}

.center-content {
  display: grid;
  position: absolute;
  gap: 0.75em;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-sizing: border-box;
  justify-content: center;
  align-items: center;
}

.center-content .iconify {
  color: #E3E3E3;
  width: 7.5rem;
  height: 7.5rem;
  justify-self: center;
  align-self: center;
}

.center-content h1 {
  color: #E3E3E3;
  font-family: "Space Grotesk";
  font-weight: 500;
  font-size: 2.5rem;
  text-align: center;
  margin: 0.5rem;
}

.center-content span {
  color: #636363;
  font-family: "Oswald";
  font-weight: 400;
  font-size: 1.5rem;
  text-align: center;
}

.center-content a {
  display: grid;
  flex-direction: row;
  box-sizing: border-box;
  width: 100%;
  padding: 1rem;
  height: fit-content;
  justify-content: center;
  align-items: center;
  border-radius: 14px;
  background-color: #2D2D2D;
  outline: 0.15rem solid #404040;
  color: #E3E3E3;
  text-align: center;
  gap: 0.2em;
}

.center-content a h1 {
  display: flex;
  font-size: 1.5rem;
  font-family: "Space Grotesk";
  font-weight: 500;
  color: #E3E3E3;
  gap: 0.75rem;
  margin: 0;
  align-items: center;
}

.center-content a h1 .iconify {
  color: #E3E3E3;
  width: 2.5rem;
  height: 2.5rem;
  justify-self: center;
  align-self: center;
}

.center-content input {
  resize: none;
  box-sizing: border-box;
  width: 100%;
  border-radius: 12px;
  background-color: #2D2D2D;
  outline: 0.15rem solid #404040;
  padding:0.7rem;
  border: none;
  color: #E3E3E3;
  font-size: 1.2rem;
}

.lcont, .rcont, .vcont {
  box-sizing: border-box;
}

.lcont, .rcont {
  width: 50vw;
  height: 100svh;
  position: relative;
  padding: 2em;
  overflow: hidden;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  z-index: 2;
}

.lcont { float: left; }
.rcont { float: right; }


.v-enter-active,
.v-leave-active {
  transition: all 0.7s ease-out;
}

.v-enter-from {
  transform: translate(150%, -50%);
}

.v-leave-to {
  transform: translate(-250%, -50%);
}
</style>
