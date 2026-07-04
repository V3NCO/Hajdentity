export default defineNuxtRouteMiddleware(async () => {
  const auth = useAuth()

  if (auth.loading.value && import.meta.client) {
    await new Promise<void>((resolve) => {
      const stop = watch(() => auth.loading.value, (val) => {
        if (!val) { stop(); resolve() }
      })
    })
  }

  if (auth.isAuthenticated.value) {
    return navigateTo('/')
  }
})
