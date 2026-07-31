<script setup lang="ts">
const secret = ref(false)
let buffer = ''
const fileError = ref('')
const preview = ref('')
const dragging = ref(false)
const fileInput = ref<HTMLInputElement>()
const pfpFileError = ref('')
const pfpPreview = ref('')
const pfpDragging = ref(false)
const pfpFileInput = ref<HTMLInputElement>()
const submitting = ref(false)
import '~/assets/css/cards.css'


definePageMeta({ middleware: 'auth', ssr: false })
useSeoMeta({
  title: 'New Plushie',
})
useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: { style: 'overflow: hidden; font-family: "Space Grotesk";' }
})

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
  species: computed(() => species.value.find(s => s.id === selectedspecies.value)?.label),
  emoji: computed(() => species.value.find(s => s.id === selectedspecies.value)?.emoji)
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

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) getFile(file)
}

function onPfpFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) getPfpFile(file)
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

async function onSubmit() {
  const file = fileInput.value?.files?.[0]
  if (!file) {
    fileError.value = 'Image is required'
    return
  }

  const pfpFile = pfpFileInput.value?.files?.[0]
  if (!pfpFile) {
    pfpFileError.value = 'Profile picture is required'
    return
  }

  submitting.value = true
  fileError.value = ''
  pfpFileError.value = ''

  const form = new FormData()
  form.append('image', file)
  form.append('pfp', pfpFile)
  for (const [key, val] of Object.entries(state)) {
    if (val !== undefined && val !== '') form.append(key, String(val))
  }

  try {
    const res = await $fetch('/api/hajs', {
      method: 'POST',
      body: form,
      credentials: 'include'
    })
    console.log(res)
    submitting.value = false
    await navigateTo('/dashboard/plushies')
  } catch (e: any) {
    fileError.value = e?.data?.detail || 'Upload failed'
    submitting.value = false
  }
}

</script>

<template>
<div class="lcont">
  <div class="vcont">
    <h1>New Plush</h1>
    <form @keydown="onKeydown" @submit.prevent="onSubmit" ref="registerForm" autocomplete="off" data-1p-ignore data-bwignore data-lpignore="true" data-form-type="other">
      <h2 style="margin: 0.25em;"><span style="color: dimgrey; font-weight: 300;">1.</span> Tell us about your companion :3</h2>
      <div class="field">
        <input
          id="username"
          v-model="state.username"
          name="username"
          type="text"
          placeholder=" "
          minlength="3"
          maxlength="96"
          pattern="(?:[a-z0-9_]|-){3,48}"
          required
        />
        <label for="name">Username *</label>
      </div>
      <div class="field">
        <input
          id="displayname"
          v-model="state.displayname"
          name="displayname"
          type="text"
          placeholder=" "
          minlength="3"
          maxlength="96"
          pattern="(?:[A-Za-z0-9_]|-){3,48}"
          required
        />
        <label for="name">Display Name *</label>
      </div>
      <div class="field">
        <select
          id="species"
          v-model="selectedspecies"
          required
        >
          <option
            v-for="option in species"
            :key="option.label"
            :value="option.id"
          >{{option.emoji}} {{option.label}}</option>
        </select>
        <label for="species">Species *</label>
      </div>
      <div class="half">
        <div class="field">
          <input
            id="date"
            v-model="state.date"
            name="date"
            type="date"
            required
          />
          <label for="date">Date of Adoption *</label>
        </div>

        <div class="field">
          <input
            id="size"
            v-model="state.size"
            name="size"
            placeholder="55cm or 100cm"
            type="number"

            required
          />
          <label for="size">Size *</label>
          <span class="unit">cm</span>
        </div>
      </div>

      <div class="field">
        <textarea
          id="description"
          v-model="state.description"
          name="description"
          rows="3"
          placeholder=" "
          required
        />
        <label for="description">Description *</label>
      </div>

      <div class="field">
        <input
          id="location"
          v-model="state.location"
          name="location"
          placeholder="IKEA San Francisco"
          type="text"
        />
        <label for="location">Location</label>
      </div>

      <div class="half">
        <div class="field">
          <input
            id="gender"
            v-model="state.gender"
            name="gender"
            type="text"
          />
          <label for="gender">Gender</label>
        </div>
        <div class="field">
          <input
            id="pronouns"
            v-model="state.pronouns"
            name="pronouns"
            type="text"
          />
          <label for="pronouns">Pronouns</label>
        </div>
      </div>

      <div class="field">
        <input
          id="lastwashed"
          v-model="state.lastwashed"
          name="lastwashed"
          type="datetime-local"
          placeholder=""
       />
        <label for="lastwashed">Last wash</label>
      </div>

      <div class="half">
        <div class="field">
          <input
            id="floof"
            name="floof"
            v-model="state.floof"
            placeholder="1 to 10"
            type="number"
            min="1"
            max="10"
          />
          <label for="floof">Fluffiness rating</label>
        </div>

        <div class="field">
          <input
            id="squish"
            v-model="state.squish"
            name="squish"
            placeholder="1 to 10"
            type="number"
            min="1"
            max="10"
          />
          <label for="squish">Squishiness</label>
        </div>
      </div>

      <div class="field" v-if="secret">
        <input
          id="mloftearsabsorbed"
          v-model="state.mloftearsabsorbed"
          name="mloftearsabsorbed"
          type="number"
        />
        <label for="mloftearsabsorbed">mL of tears absorbed</label>
      </div>

      <h2 style="margin: 0.25em;"><span style="color: dimgrey; font-weight: 300;">2.</span> Show us what your plush looks like!</h2>
      <div
        class="field file-field"
        :class="{ dragging: dragging }"
        @dragenter.prevent="dragging = true"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <input
          ref="fileInput"
          id="image"
          name="image"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          @change="onFileChange"
          required
        />
        <label for="image">Click or Drag here</label>
        <p class="imgrec">(Max 10MB, PNG, JPEG, WEBP and GIF supported, 4:3 or 1:2 recommended)</p>
        <span class="file-error" v-if="fileError">{{ fileError }}</span>
      </div>

      <h2 style="margin: 0.25em;"><span style="color: dimgrey; font-weight: 300;">3.</span> Upload a pfp for your companion :3</h2>

      <div
        class="field file-field"
        :class="{ dragging: pfpDragging }"
        @dragenter.prevent="pfpDragging = true"
        @dragover="onPfpDragOver"
        @dragleave="onPfpDragLeave"
        @drop="onPfpDrop"
      >
        <input
          ref="pfpFileInput"
          id="pfp"
          name="pfp"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          @change="onPfpFileChange"
          required
        />
        <label for="pfp">Click or Drag here</label>
        <p class="imgrec">(Max 10MB, 1:1 square aspect ratio required for profile pic)</p>
        <span class="file-error" v-if="pfpFileError">{{ pfpFileError }}</span>
      </div>

      <button type="submit">Submit</button>
    </form>
  </div>
</div>
<div class="rcont">
  <h1>Previews</h1>
  <div class="vrcont">
    <div
      :style="{ backgroundImage: `url(${preview})`, width: `20rem` }"
      class="card"
    >
      <div class="gradient">
        <h1>{{ state.displayname }}</h1>
        <span>
          <p>{{ state.pronouns }}</p>
        </span>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.lcont, .rcont, .vcont {
  box-sizing: border-box;
}

.lcont, .rcont {
  width: 50vw;
  height: 100svh;
  position: relative;
  padding: 1em;
  overflow: hidden;
  box-sizing: border-box;
}

.lcont { float: left; }
.rcont { float: right; }

.vrcont {
  padding: 1em;
  height: fit-content;
  max-width: 100%;
  background-image: linear-gradient(147deg, #9FB2CACC, #5D7798CC);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.vcont {
  padding: 1em;
  height: 100%;
  width: 100%;
  overflow-y: auto;
  background-image: linear-gradient(147deg, #9FB2CACC, #5D7798CC);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

h1 {
  margin: 0.25em;
}

input,
select,
textarea {
  border-radius: 1rem;
  border: 2px solid #95ADB6;
  background-color: #C3D0D5;
  font-weight: 600;
  color: black;
}

form {
  display: flex;
  flex-direction: column;
  margin-top: 1.5rem;
  gap: 1rem;
  width: 100%;
}

.field {
  position: relative;
}

.field input,
.field select,
.field textarea{
  height: 3rem;
  width: 100%;
  padding: 1rem 0.75rem 0.25rem 0.9rem;
  box-sizing: border-box;
}

.field input[type="number"] {
  -moz-appearance: textfield;
}

.field input[type="number"]::-webkit-outer-spin-button,
.field input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.field .unit {
  position: absolute;
  right: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  color: #3A4A5A;
  font-weight: 600;
  pointer-events: none;
}

.field label {
  position: absolute;
  left: 1.1rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  font-weight: 500;
  color: #4A5A6A;
  pointer-events: none;
  transition: all 0.15s ease-out;
}

.field input:focus + label,
.field input:not(:placeholder-shown) + label,
.field select:focus + label,
.field select:not(:placeholder-shown) + label,
.field textarea:focus + label,
.field textarea:not(:placeholder-shown) + label{
  top: 0.7rem;
  font-size: 0.7rem;
  color: #2A3A4A;
  font-weight: 700;
}

form input {
  max-width: 100%;
}

form button {
  margin-top: 0.5em;
  width: 100%;
  height: 2.5rem;
}

button {
  border-radius: 1rem;
  border: 2px solid #95ADB6;
  background-color: #C3D0D5;
  font-weight: 700;
}

button:hover {
  border: 3px solid #95ADB6;
  background-color: #E3F0F5;
}

button:active {
  border: 3px solid #859DA6;
  background-color: #A3B0B5;
}

input:user-invalid,
textarea:user-invalid {
  border: 2px solid #EF959C;
  background-color: #F7CACE;
}

.half {
  display: flex;
  gap: 1rem;
}

.half .field {
  flex: 1;
}

#description {
  height: 4.5rem;
  resize: none;
}

.file-field {
  border: 2px dashed gray;
  border-radius: 1.5rem;
  margin-bottom: 2rem;
}

.file-field.dragging {
  background-color: #FFFFFF0F;
}

.field input[type="file"] {
  height: 100%;
  font-size: 0.82rem;
  font-weight: 500;
  color: dimgray;
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
  left: 50%;
  transform: translateX(-50%);
  background: #F7CACE;
  color: #D94A4A;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.8rem;
  border-radius: 1rem;
}

.imgrec {
  margin-top: 0.5em;
}



.toggle {
    border: 0.2rem solid #95adb6;
    border-radius: calc( 2.5rem / 2 );
    width: 4.5rem;
    height: 2.5rem;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    transition: transform 0.07s;
    cursor: pointer;
}

.toggle::after {
    content: "";
    display: inline-block;
    margin: 0.2rem;
    border-radius: 50%;
    width: 1.7rem;
    height: 1.7rem;
    background: #31404f;
    transition: transform 0.07s linear;
}

.toggle:checked::after {
    transform: translateX(2rem);
}

.toggle:hover {
    transform: scale(1.07);
}

.toggle:active {
    transform: scale(1.0);
}

.toggle:focus {
    outline: none;
    box-shadow: 0 0 0 0.2rem rgba(255,255,255,0.4);
}

@media screen and (max-width: 790px) {
	.lcont {
	  width: 100vw
	}
}
</style>
