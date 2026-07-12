export const useAuth = () => {
  const user = useState<{ username: string; email: string; disabled: boolean } | null>('auth:user', () => null)
  const loading = useState('auth:loading', () => true)

  const fetchUser = async () => {
    try {
      const res = await $fetch<{ username: string; email: string; disabled: boolean }>('/api/auth/me', {
        credentials: 'include',
      })
      user.value = { username: res.username, email: res.email, disabled: res.disabled }
    } catch {
      user.value = null
    } finally {
      loading.value = false
    }
  }

  const login = async (username: string, password: string) => {
    const formBody = new URLSearchParams({ username, password })
    await $fetch('/api/auth/token', {
      method: 'POST',
      body: formBody.toString(),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      credentials: 'include',
    })
    await fetchUser()
  }

  const logout = async () => {
    await $fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    }).catch(() => {})
    user.value = null
    await navigateTo('/login')
  }

  const isAuthenticated = computed(() => !!user.value && !user.value.disabled)

  return { user, loading, fetchUser, login, logout, isAuthenticated }
}
