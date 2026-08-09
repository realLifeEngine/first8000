const THEME_COOKIE_NAME = 'kaku_theme'

export function getStoredTheme(defaultTheme = 'light') {
  if (typeof document === 'undefined') return defaultTheme

  const match = document.cookie.match(new RegExp(`(?:^|; )${THEME_COOKIE_NAME}=([^;]*)`))
  const cookieTheme = match?.[1]

  if (cookieTheme === 'light' || cookieTheme === 'dark') {
    return cookieTheme
  }

  return defaultTheme
}

export function setTheme(theme) {
  if (typeof document === 'undefined') return

  document.documentElement.setAttribute('data-theme', theme)
  const expires = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toUTCString()
  document.cookie = `${THEME_COOKIE_NAME}=${theme}; expires=${expires}; path=/; SameSite=Lax`
}

export function initTheme(defaultTheme = 'light') {
  const theme = getStoredTheme(defaultTheme)
  setTheme(theme)
  return theme
}
