export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return

  const auth = useAuth()

  if (auth.loading.value) {
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
