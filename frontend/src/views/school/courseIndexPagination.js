export function createRequestGuard() {
  let currentToken = 0

  return {
    beginRequest() {
      currentToken += 1
      return currentToken
    },
    invalidate() {
      currentToken += 1
    },
    isCurrent(token) {
      return token === currentToken
    },
  }
}

export function scrollToTop() {
  if (typeof window !== 'undefined' && typeof window.scrollTo === 'function') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
