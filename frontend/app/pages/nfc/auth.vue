<script setup>
const route = useRoute()
const { uid, ctr, mac } = route.query

const { data, error } = await useFetch('/api/nfc/auth', {
  method: 'POST',
  body: {
    uid: uid,
    ctr: parseInt(ctr, 16),
    mac: mac
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
