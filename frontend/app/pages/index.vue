<script setup lang="ts">
const auth = useAuth()

if (import.meta.client) {
  if (auth.loading.value) {
    await new Promise<void>((resolve) => {
      const stop = watch(() => auth.loading.value, (val) => {
        if (!val) {
          stop()
          resolve()
        }
      })
    })
  }

  await navigateTo(auth.isAuthenticated.value ? '/dashboard' : '/login')
}
</script>

<template>

</template>
