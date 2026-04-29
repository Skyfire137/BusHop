import { describe, it, expect } from 'vitest'
import { buildAffiliateUrl } from './affiliate'

describe('buildAffiliateUrl', () => {
  const BASE_URL = 'https://booking.example.com/tickets'

  it('appends ref param with operator code', () => {
    const result = buildAffiliateUrl('vexere', BASE_URL)
    expect(new URL(result).searchParams.get('ref')).toBe('vexere')
  })

  it('appends utm_source=bushop', () => {
    const result = buildAffiliateUrl('vexere', BASE_URL)
    expect(new URL(result).searchParams.get('utm_source')).toBe('bushop')
  })

  it('preserves the original host', () => {
    const result = buildAffiliateUrl('vexere', BASE_URL)
    expect(new URL(result).host).toBe('booking.example.com')
  })

  it('preserves the original pathname', () => {
    const result = buildAffiliateUrl('vexere', BASE_URL)
    expect(new URL(result).pathname).toBe('/tickets')
  })

  it('preserves pre-existing query params', () => {
    const urlWithParams = 'https://booking.example.com/tickets?seat=VIP'
    const result = buildAffiliateUrl('partner', urlWithParams)
    const parsed = new URL(result)
    expect(parsed.searchParams.get('seat')).toBe('VIP')
    expect(parsed.searchParams.get('ref')).toBe('partner')
  })

  it('handles operator codes with special characters via URL encoding', () => {
    const result = buildAffiliateUrl('op code+test', BASE_URL)
    // URL encodes the value; decoding it back gives the original string
    expect(new URL(result).searchParams.get('ref')).toBe('op code+test')
  })
})
