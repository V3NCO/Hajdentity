<script setup lang="ts">
import { useApi } from '~/lib/api'

const pfpFileError = ref('')
const pfpPreview = ref('')
const pfpDragging = ref(false)
const pfpFileInput = ref<HTMLInputElement>()
const fileError = ref('')
const preview = ref('')
const dragging = ref(false)
const fileInput = ref<HTMLInputElement>()
const submitting = ref(false)
const nfc = ref()

const selectedspecies = ref('haj')
const species = ref([
  {emoji: '🦈', label: 'Blåhaj', id: 'haj'},
  {emoji: '🐙', label: 'Blåvingad', id: 'blavinsquid'},
  {emoji: '🐋', label: 'Blåvingad', id: 'blavinwhale'},
  {emoji: '🧸', label: 'Djungelskog', id: 'bearskog'},
  {emoji: '🐒', label: 'Djungelskog', id: 'monkskog'},
  {emoji: '🦁', label: 'Djungelskog', id: 'lionskog'},
  {emoji: '🐝', label: 'Skogsduva', id: 'bee2bee'},
  {emoji: '🐼', label: 'Kramig', id: 'kramig'},
  {emoji: '👽', label: 'Aftonsparv', id: 'aftonsparv'},
  {emoji: '🧸', label: 'Grejsimojs', id: 'grejsimojs'},
  {emoji: '🐕', label: 'Gosig Golden', id: 'woof'},
  {emoji: '🦛', label: 'Sandalöpare', id: 'sandalopare'}
])

useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: { style: 'overflow: hidden; background-color: #212121; background-repeat: no-repeat; background-size: cover;' }
})

const api = useApi()
const route = useRoute()

let buffer = ''
const secret = ref(false)
const loading = ref(true)

const plushdata = ref()
const plusherror = ref()

const state = reactive({
  displayname: undefined,
  username: undefined,
  date: undefined,
  size: undefined,
  description: undefined,
  location: undefined,
  gender: undefined,
  pronouns: undefined,
  lastwashed: undefined,
  floof: undefined,
  squish: undefined,
  mloftearsabsorbed: undefined,
})


function onKeydown(e: KeyboardEvent) {
  buffer += e.key.toLowerCase()
  buffer = buffer.slice(-3)
  if (buffer === 'sad') secret.value = true
}

function getFile(file: File) {
  fileError.value = ''

  if (file.size > 10 * 1024 * 1024) {
    fileError.value = 'Max 10MB'
    preview.value = ''
    return
  }

  const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  if (!allowed.includes(file.type)) {
    fileError.value = 'JPEG, PNG, WebP, or GIF only'
    preview.value = ''
    return
  }

  const img = new Image()
  preview.value = URL.createObjectURL(file)
  img.src = preview.value
}

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) getFile(file)
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  dragging.value = true
}

function onDragLeave() {
  dragging.value = false
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  const dt = new DataTransfer()
  dt.items.add(file)
  if (fileInput.value) fileInput.value.files = dt.files
  getFile(file)
}

async function onSubmit() {
  const file = fileInput.value?.files?.[0]
  const pfpFile = pfpFileInput.value?.files?.[0]


  submitting.value = true
  fileError.value = ''
  pfpFileError.value = ''
  const selected = species.value.find(s => s.id === selectedspecies.value)
  const form = new FormData()
  if (file) {form.append('image', file)}
  if (pfpFile) {form.append('pfp', pfpFile)}
  if (selected?.emoji !== undefined && selected?.emoji !== '' ) {form.append('emoji', String(selected?.emoji))}
  if (selected?.label !== undefined && selected?.label !== '') {form.append('species', String(selected?.label))}

  for (const [key, val] of Object.entries(state)) {
    if (val !== undefined && val !== '') form.append(key, String(val))
  }

  const {data, error} = await api.PATCH('/api/hajs/{haj_id}',
    {
      params: {
        path: {
          haj_id: route.params.id as string
        }
      },
      body: form
    })

  console.log(data)
  submitting.value = false
  await navigateTo('/dashboard/plushies')
}

function getPfpFile(file: File) {
  pfpFileError.value = ''

  if (file.size > 10 * 1024 * 1024) {
    pfpFileError.value = 'Max 10MB'
    pfpPreview.value = ''
    return
  }

  const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
  if (!allowed.includes(file.type)) {
    pfpFileError.value = 'JPEG, PNG, WebP, or GIF only'
    pfpPreview.value = ''
    return
  }

  const img = new Image()
  pfpPreview.value = URL.createObjectURL(file)
  img.onload = () => {
    if (img.naturalWidth !== img.naturalHeight) {
      pfpFileError.value = 'Must be 1:1 square aspect ratio'
      pfpPreview.value = ''
      return
    }
  }
  img.src = pfpPreview.value
}

function onPfpFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) getPfpFile(file)
}

function onPfpDragOver(e: DragEvent) {
  e.preventDefault()
  pfpDragging.value = true
}

function onPfpDragLeave() {
  pfpDragging.value = false
}

function onPfpDrop(e: DragEvent) {
  e.preventDefault()
  pfpDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (!file) return
  const dt = new DataTransfer()
  dt.items.add(file)
  if (pfpFileInput.value) pfpFileInput.value.files = dt.files
  getPfpFile(file)
}

async function onNFC() {
  navigateTo(`/dashboard/plushies/nfc?haj=${route.params.id}`)
}

async function delNFC() {
  await api.DELETE('/api/nfc/{haj_id}',
    {
      params: {
        path: {
          haj_id: route.params.id as string
        }
      },
    }
  )
}

async function delHaj() {
  await api.DELETE(
    '/api/hajs/{haj_id}',
    { params: { path: { haj_id: route.params.id as string } } }
  )
}

onMounted(async () => {
  const { data: hajData, error: err } = await api.GET(
    '/api/hajs/{haj_id}',
    { params: { path: { haj_id: route.params.id as string } } }
  )
  const { data: nfcData, error: nfcerr } = await api.GET(
    '/api/nfc/{haj_id}',
    { params: { path: { haj_id: route.params.id as string } } }
  )
  plushdata.value = hajData?.haj
  nfc.value = nfcData
  plusherror.value = err
  selectedspecies.value = String(species.value.find(s => s.label === hajData?.haj.species)?.id)
  loading.value = false
})
</script>
<template>
<Transition><div v-if="loading" class="loading">
  <h1>Loading...</h1>
  <video autoplay loop muted playsinline>
    <source src="/blahaj.webm" type="video/webm">
  </video>
</div></Transition>
<div class="midcont" v-if="!loading">
  <div class="act-topline">
    <div class="act-pfp" :style="{ backgroundImage: `url(/api/hajs/${route.params.id}/pfp)` }"></div>
    <div class="act-title">
       <h1>{{plushdata?.displayname}} <span class="act-pronouns">{{plushdata?.pronouns}}</span></h1>
       <h2 class="act-username">@{{plushdata?.username}}</h2>
       <p>{{plushdata?.description}}</p>
    </div>
  </div>
  <div class="warning" v-if="!nfc.is_setup">
    <h2>Setup an NFC Tag!</h2>
    <p>
      Hey! You haven't set up an NFC tag for this plush yet!
      Consider doing so, if you don't know, the type of tag to use is the NTAG 424 DNA.
    </p>
    <button @click="onNFC" class="button"><h3>Setup NFC</h3></button>
  </div>
  <button v-else @click="delNFC" class="button del">
    <h1><Icon name="material-symbols:nfc"/>Delete NFC</h1>
  </button>
  <button @click="delHaj" class="button del">
    <h1><Icon name="hajdentity:haj"/>Delete Plush</h1>
  </button>
  <form class="posting" @keydown="onKeydown" @submit.prevent="onSubmit">
    <div class="field">
      <input
        id="displayname"
        v-model="state.displayname"
        name="displayname"
        type="text"
        minlength="3"
        maxlength="96"
        pattern="(?:[A-Za-z0-9_]|-){3,48}"
        :placeholder="plushdata?.displayname"
      />
      <label for="name">Display Name</label>
    </div>
    <div class="field">
      <select
        id="species"
        v-model="selectedspecies"
      >
        <option
          v-for="option in species"
          :key="option.label"
          :value="option.id"
        >{{option.emoji}} {{option.label}}</option>
      </select>
      <label for="species">Species *</label>
    </div>
    <div class="field">
      <input
        id="date"
        v-model="state.date"
        name="date"
        type="date"
        :placeholder="plushdata?.date"
      />
      <label for="date">Date of Adoption</label>
    </div>

    <div class="field">
      <input
        id="size"
        v-model="state.size"
        name="size"
        type="number"
        :placeholder="plushdata?.size+`cm`"
      />
      <label for="size">Size</label>
    </div>

    <div class="field">
      <textarea
        id="description"
        v-model="state.description"
        name="description"
        rows="3"
        :placeholder="plushdata?.description"
      />
      <label for="description">Description</label>
    </div>

    <div class="field">
      <input
        id="location"
        v-model="state.location"
        name="location"
        type="text"
        :placeholder="plushdata?.location"
      />
      <label for="location">Location</label>
    </div>

    <div class="field">
      <input
        id="gender"
        v-model="state.gender"
        name="gender"
        type="text"
        :placeholder="plushdata?.gender"
      />
      <label for="gender">Gender</label>
    </div>
    <div class="field">
      <input
        id="pronouns"
        v-model="state.pronouns"
        name="pronouns"
        type="text"
        :placeholder="plushdata?.pronouns"
      />
      <label for="pronouns">Pronouns</label>
    </div>

    <div class="field">
      <input
        id="lastwashed"
        v-model="state.lastwashed"
        name="lastwashed"
        type="datetime-local"
        :placeholder="plushdata?.lastwashed"
      />
      <label for="lastwashed">Last wash</label>
    </div>

    <div class="field">
      <input
        id="floof"
        name="floof"
        v-model="state.floof"
        type="number"
        min="1"
        max="10"
        :placeholder="plushdata?.floof"
      />
      <label for="floof">Fluffiness rating</label>
    </div>

    <div class="field">
      <input
        id="squish"
        v-model="state.squish"
        name="squish"
        type="number"
        min="1"
        max="10"
        :placeholder="plushdata?.floof"
      />
      <label for="squish">Squishiness</label>
    </div>

    <div class="field" v-if="secret">
      <input
        id="mloftearsabsorbed"
        v-model="state.mloftearsabsorbed"
        name="mloftearsabsorbed"
        :placeholder="plushdata?.mloftearsabsorbed"
        type="number"
      />
      <label for="mloftearsabsorbed">mL of tears absorbed</label>
    </div>

    <div
      class="field file-field"
      :class="{ dragging: dragging }"
      @dragenter.prevent="dragging = true"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
      :style="{ backgroundImage: `url(${preview})`}"
    >
      <input
        ref="fileInput"
        id="image"
        name="image"
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        @change="onFileChange"
      />
      <label for="image">Click or Drag here</label>
      <p class="imgrec">(Max 10MB, PNG, JPEG, WEBP and GIF supported, 4:3 or 1:2 recommended)</p>
      <span class="file-error" v-if="fileError">{{ fileError }}</span>
    </div>


    <div
      class="field file-field"
      :class="{ dragging: pfpDragging }"
      @dragenter.prevent="pfpDragging = true"
      @dragover="onPfpDragOver"
      @dragleave="onPfpDragLeave"
      @drop="onPfpDrop"
      :style="{ backgroundImage: `url(${pfpPreview})`}"
    >
      <input
        ref="pfpFileInput"
        id="pfp"
        name="pfp"
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        @change="onPfpFileChange"
      />
      <label for="pfp">Click or Drag here</label>
      <p class="imgrec">(Max 10MB, 1:1 square aspect ratio required for profile pic)</p>
      <span class="file-error" v-if="pfpFileError">{{ pfpFileError }}</span>
    </div>
    <button type="submit" class="btn" :disabled="submitting">
      <h1><Icon name="material-symbols:arrow-circle-up-outline"/>{{ submitting ? 'Updating...' : 'Update' }}</h1>
    </button>
  </form>
</div>
</template>

<style>
.button {
  flex-grow:1;
  display: grid;
  justify-content: center;
  align-items: center;
  border: none;
  border-radius: 10px;
  width: 10rem;
  background-color: #2D2D2D;
  outline: 0.15rem solid #404040;
  box-sizing: border-box;
  color: #E3E3E3;
  text-align: center;
  gap: 0.2em;
}

.button h1 {
  margin: 0;
  display: flex;
  gap: 0.3em;
  align-items: center;
}

.del {
  width: 100%;
  padding: 0.5rem;
  background-color: #EE4444A0;
  outline: 0.15rem dashed #EE4444;
}


.button:hover {
  outline: 0.15rem solid #636363;
  background-color: #404040;
}

.button:active {
  outline: 0.15rem solid #636363;
  background-color: #636363;
}

.warning {
  border: 3px dashed #ff9900;
  border-radius: 18px;
  background-color: #ff990040;
  color: #ff9900;
  padding: 1em;
}

.warning h2 {
  margin: 0;
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
  overflow-y: scroll;
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

.posting {
  display: flex;
  flex-direction: column;
  gap: 2.3em;
}

.posting textarea {
  resize: none;
  box-sizing: border-box;
  width: 100%;
  border-radius: 18px;
  background-color: #2D2D2D;
  outline: 0.15rem solid #404040;
  padding: 1rem;
  border: none;
  color: #E3E3E3;
  font-size: 1.2rem;
}

.posting input {
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

.posting select {
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

.posting button {
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

.posting button h1 {
  display: flex;
  font-size: 1.5rem;
  font-family: "Space Grotesk";
  font-weight: 500;
  color: #E3E3E3;
  gap: 0.75rem;
  margin: 0;
  align-items: center;
}

.file-field {
  border: 2px dashed gray;
  border-radius: 1.5rem;
  margin-bottom: 2rem;
  background-size: cover;
  background-position: center;
}

.file-field.dragging {
  background-color: #FFFFFF0F;
}

.field input[type="file"] {
  height: 100%;
  opacity: 0;
}

.file-field label {
  position: absolute !important;
  left: 50% !important;
  top: 50% !important;
  transform: translate(-50%, -50%) !important;
  font-size: 0.9rem !important;
  color: dimgray !important;
}

.file-error {
  position: absolute;
  bottom: 0.3rem;
  background: #F7CACE;
  color: #D94A4A;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.8rem;
  border-radius: 1rem;
}

.imgrec {
  margin-top: 0.5em;
  color: #636363
}


.field {
  position: relative;
}

.field label {
  position: absolute;
  left: 0.8rem;
  top: -0.8rem;
  transform: translateY(-50%);
  font-size: 0.9rem;
  font-weight: 500;
  color: #636363;
}

@media screen and (max-width: 500px) {
  .act-topline {
    height: 15svh;
    max-height: 15svh;
    gap: 2rem;
    font-weight: 500;
  }

  .act-topline h1 {
    font-size: 1.5rem;
    color: #E3E3E3;
    gap: 1rem;
    margin: 0;
  }

  .act-pfp {
    aspect-ratio: 1 / 1;
    border-radius: 20px;
  }

  .act-username {
    font-family: "Space Grotesk";
    font-weight: 300;
    color: #E3E3E3;
    font-size: 1.2rem;
    margin-top: 0;
  }

  .act-pronouns {
    font-size: 0.9rem;
  }
}
</style>
