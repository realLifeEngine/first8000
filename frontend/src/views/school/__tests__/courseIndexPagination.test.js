import { describe, it, expect, vi } from 'vitest'
import { createRequestGuard, scrollToTop } from '../courseIndexPagination'

describe('createRequestGuard', () => {
  it('keeps only the latest request active', () => {
    const guard = createRequestGuard()

    const firstRequest = guard.beginRequest()
    const secondRequest = guard.beginRequest()

    expect(guard.isCurrent(firstRequest)).toBe(false)
    expect(guard.isCurrent(secondRequest)).toBe(true)
  })

  it('invalidates older requests when switching products', () => {
    const guard = createRequestGuard()
    const firstRequest = guard.beginRequest()
    guard.invalidate()
    const secondRequest = guard.beginRequest()

    expect(guard.isCurrent(firstRequest)).toBe(false)
    expect(guard.isCurrent(secondRequest)).toBe(true)
  })

  it('scrolls the browser window to the top', () => {
    const scrollToSpy = vi.fn()
    Object.defineProperty(globalThis, 'window', {
      value: { scrollTo: scrollToSpy },
      configurable: true,
    })

    scrollToTop()

    expect(scrollToSpy).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' })
  })
})
