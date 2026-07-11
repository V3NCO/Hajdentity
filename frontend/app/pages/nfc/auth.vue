<script setup lang="ts">
const route = useRoute()
const { picc_data, cmac } = route.query

useHead({ htmlAttrs: { lang: 'en' }})


const haj = ref()
onMounted(async () => {
  try {
    const res = await $fetch<{ status: string; haj: string }>('/api/nfc/auth', {
      method: 'POST',
      body: {picc_data, cmac},
      credentials: 'include'
    })
    haj.value = res.haj
    await navigateTo(`/plush/${haj.value}/act`)
  } catch (e) {
    alert((e as any)?.response?._data?.detail || (e as any)?.data?.detail || 'An error occured')
  }
})
</script>

<template>
<Transition><div class="loading">
  <h1>Loading...</h1>
  <video autoplay loop muted playsinline>
    <source src="/blahaj.webm" type="video/webm">
  </video>
</div></Transition>
</template>
