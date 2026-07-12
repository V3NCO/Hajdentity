<script setup lang="ts">
import { useApi } from '~/lib/api'

const fileError = ref('')
const preview = ref('')
const dragging = ref(false)
const fileInput = ref<HTMLInputElement>()
const submitting = ref(false)

useHead({
  htmlAttrs: { lang: 'en' },
  bodyAttrs: { style: 'overflow: hidden; background-color: #212121; background-repeat: no-repeat; background-size: cover;' }
})
const api = useApi()
const route = useRoute()

const loading = ref(true)

const plushdata = ref()
const plusherror = ref()

const state = reactive({
  note: undefined,
  cw: undefined,
  location: undefined,
  alt_text: undefined
})

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
  if (!file) {
    fileError.value = 'Image is required'
    return
  }

  submitting.value = true
  fileError.value = ''

  const form = new FormData()
  form.append('image', file)
  for (const [key, val] of Object.entries(state)) {
    if (val !== undefined && val !== '') form.append(key, String(val))
  }

  const { data: res, error: err } = await api.POST(
    '/api/hajs/{haj_id}/posts',
    {
      params: { path: { haj_id: route.params.id as string } },
      body: form as any,
    },
  )
  plusherror.value = err
  submitting.value = false
}

onMounted(async () => {
  const { data: hajData, error: err } = await api.GET(
    '/api/hajs/{haj_id}',
    { params: { path: { haj_id: route.params.id as string } } }
  )
  plushdata.value = hajData?.haj
  plusherror.value = err
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
  <form class="posting" @submit.prevent="onSubmit">
    <div class="field">
      <label for="note">Note</label>
      <textarea
        name="note"
        rows="3"
        v-model="state.note"
        placeholder="Tip: You can @username other plushies!"
        required
      />
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
        required
      />
      <label for="image">Click or Drag here</label>
      <p class="imgrec">(Max 10MB, PNG, JPEG, WEBP and GIF supported)</p>
      <span class="file-error" v-if="fileError">{{ fileError }}</span>
    </div>
    <div class="field">
      <label for="note">Alt Text for image</label>
      <input
        name="alt_text"
        type="text"
        v-model="state.alt_text"
        placeholder=""
      />
    </div>
    <div class="field">
      <label for="location">Location (Optional)</label>
      <input
        name="location"
        v-model="state.location"
        placeholder="London, England"
      />
    </div>
    <div class="field">
      <label for="cw">Content warning (Optional, will mark the post as restricted/NSFW)</label>
      <input
        name="cw"
        v-model="state.cw"
        placeholder=""
      />
    </div>
    <button type="submit" class="btn" :disabled="submitting">
      <h1><Icon name="material-symbols:arrow-circle-up-outline"/>{{ submitting ? 'Posting...' : 'Post' }}</h1>
    </button>
  </form>
</div>
</template>

<style>
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
