<script setup>
const route = useRoute()
const { picc_data, cmac } = route.query

const { data, error } = await useFetch('/api/nfc/auth', {
  method: 'POST',
  body: {
    picc_data: picc_data,
    cmac: cmac
  }
})

if (data.value) {
  console.log("Auth success?!111!!!!! YIPPPEEEEE")
} else {
  console.log("nope")
}
</script>

<template>

</template>
