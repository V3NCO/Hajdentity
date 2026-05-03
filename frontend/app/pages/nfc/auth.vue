<script setup>
const route = useRoute()
const { picc, cmac } = route.query

const { data, error } = await useFetch('/api/nfc/auth', {
  method: 'POST',
  body: {
    picc: picc,
    cmac: cmac
  }
})

if (data.value) {
  console.log("Auth success")
} else {
  console.log("nope")
}
</script>

<template>

</template>
