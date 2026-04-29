import { describe, it, expect } from 'vitest'
import { buildMapsDeeplink } from './maps'

describe('buildMapsDeeplink', () => {
  it('returns a string starting with the Google Maps base URL', () => {
    const result = buildMapsDeeplink(10.7769, 106.7009)
    expect(result).toMatch(/^https:\/\/maps\.google\.com\/maps/)
  })

  it('embeds latitude and longitude in the q param', () => {
    const result = buildMapsDeeplink(10.7769, 106.7009)
    expect(result).toContain('q=10.7769,106.7009')
  })

  it('works with positive coordinates (northern/eastern hemisphere)', () => {
    const result = buildMapsDeeplink(21.0285, 105.8542)
    expect(result).toBe('https://maps.google.com/maps?q=21.0285,105.8542')
  })

  it('works with negative latitude (southern hemisphere)', () => {
    const result = buildMapsDeeplink(-33.8688, 151.2093)
    expect(result).toContain('q=-33.8688,151.2093')
  })

  it('works with negative longitude (western hemisphere)', () => {
    const result = buildMapsDeeplink(40.7128, -74.006)
    expect(result).toContain('q=40.7128,-74.006')
  })

  it('works with zero coordinates (equator / prime meridian)', () => {
    const result = buildMapsDeeplink(0, 0)
    expect(result).toBe('https://maps.google.com/maps?q=0,0')
  })
})
