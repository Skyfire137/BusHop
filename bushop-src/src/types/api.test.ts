import { describe, it, expect } from 'vitest'
import type { ApiMeta, ApiResponse } from './api'
import type { ProvinceI18n, Route, RoutesResponse } from './route'
import type { Schedule, SchedulesResponse, ScheduleSearchParams } from './schedule'
import type { ScrapeJobStatus, ScrapeJob, ScrapeJobResponse, CreateScrapeJobRequest } from './scrape-job'

// ---------------------------------------------------------------------------
// ApiMeta / ApiResponse
// ---------------------------------------------------------------------------
describe('ApiMeta shape', () => {
  it('accepts scraped_at as ISO string', () => {
    const meta: ApiMeta = { scraped_at: '2026-04-29T00:00:00Z' }
    expect(typeof meta.scraped_at).toBe('string')
  })

  it('accepts scraped_at as null', () => {
    const meta: ApiMeta = { scraped_at: null }
    expect(meta.scraped_at).toBeNull()
  })
})

describe('ApiResponse shape', () => {
  it('wraps data and meta correctly', () => {
    const response: ApiResponse<number[]> = {
      data: [1, 2, 3],
      meta: { scraped_at: '2026-04-29T00:00:00Z' }
    }
    expect(Array.isArray(response.data)).toBe(true)
    expect(response.meta).toHaveProperty('scraped_at')
  })
})

// ---------------------------------------------------------------------------
// Route / ProvinceI18n / RoutesResponse
// ---------------------------------------------------------------------------
describe('ProvinceI18n shape', () => {
  it('has vi, en, ja string fields', () => {
    const province: ProvinceI18n = { vi: 'Hà Nội', en: 'Hanoi', ja: 'ハノイ' }
    expect(typeof province.vi).toBe('string')
    expect(typeof province.en).toBe('string')
    expect(typeof province.ja).toBe('string')
  })
})

describe('Route shape', () => {
  it('has all required numeric and string fields', () => {
    const route: Route = {
      id: 1,
      slug: 'hanoi-hochiminh',
      origin_id: 10,
      destination_id: 20,
      origin_name: { vi: 'Hà Nội', en: 'Hanoi', ja: 'ハノイ' },
      destination_name: { vi: 'TP. Hồ Chí Minh', en: 'Ho Chi Minh City', ja: 'ホーチミン市' }
    }
    expect(typeof route.id).toBe('number')
    expect(typeof route.slug).toBe('string')
    expect(typeof route.origin_id).toBe('number')
    expect(typeof route.destination_id).toBe('number')
    expect(route.origin_name).toHaveProperty('vi')
    expect(route.destination_name).toHaveProperty('en')
  })
})

describe('RoutesResponse shape', () => {
  it('wraps a Route array under data', () => {
    const resp: RoutesResponse = {
      data: [],
      meta: { scraped_at: null }
    }
    expect(Array.isArray(resp.data)).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// Schedule / SchedulesResponse / ScheduleSearchParams
// ---------------------------------------------------------------------------
describe('Schedule shape', () => {
  it('has all required fields with correct types', () => {
    const schedule: Schedule = {
      id: 'sch-001',
      route_id: 1,
      operator_name: 'Phương Trang',
      departure_time: '08:00',
      arrival_time: '14:00',
      price: 250000,
      scraped_at: '2026-04-29T00:00:00Z',
      is_stale: false
    }
    expect(typeof schedule.id).toBe('string')
    expect(typeof schedule.route_id).toBe('number')
    expect(typeof schedule.price).toBe('number')
    expect(typeof schedule.is_stale).toBe('boolean')
  })
})

describe('ScheduleSearchParams shape', () => {
  it('has origin_id, destination_id, date', () => {
    const params: ScheduleSearchParams = {
      origin_id: 10,
      destination_id: 20,
      date: '2026-05-01'
    }
    expect(typeof params.origin_id).toBe('number')
    expect(typeof params.destination_id).toBe('number')
    expect(typeof params.date).toBe('string')
  })
})

describe('SchedulesResponse shape', () => {
  it('wraps a Schedule array under data', () => {
    const resp: SchedulesResponse = {
      data: [],
      meta: { scraped_at: null }
    }
    expect(Array.isArray(resp.data)).toBe(true)
  })
})

// ---------------------------------------------------------------------------
// ScrapeJob / ScrapeJobStatus / ScrapeJobResponse / CreateScrapeJobRequest
// ---------------------------------------------------------------------------
describe('ScrapeJobStatus values', () => {
  const validStatuses: ScrapeJobStatus[] = ['pending', 'running', 'completed', 'failed']

  it.each(validStatuses)('"%s" is a valid ScrapeJobStatus', (status) => {
    expect(['pending', 'running', 'completed', 'failed']).toContain(status)
  })
})

describe('ScrapeJob shape', () => {
  it('accepts completed_at as null', () => {
    const job: ScrapeJob = {
      id: 'job-001',
      status: 'pending',
      route_id: 1,
      created_at: '2026-04-29T00:00:00Z',
      completed_at: null
    }
    expect(job.completed_at).toBeNull()
  })

  it('accepts completed_at as ISO string', () => {
    const job: ScrapeJob = {
      id: 'job-002',
      status: 'completed',
      route_id: 1,
      created_at: '2026-04-29T00:00:00Z',
      completed_at: '2026-04-29T00:01:00Z'
    }
    expect(typeof job.completed_at).toBe('string')
  })
})

describe('ScrapeJobResponse shape', () => {
  it('wraps a single ScrapeJob under data', () => {
    const resp: ScrapeJobResponse = {
      data: {
        id: 'job-003',
        status: 'running',
        route_id: 2,
        created_at: '2026-04-29T00:00:00Z',
        completed_at: null
      },
      meta: { scraped_at: null }
    }
    expect(resp.data).toHaveProperty('id')
    expect(resp.data).toHaveProperty('status')
  })
})

describe('CreateScrapeJobRequest shape', () => {
  it('has route_id and travel_date', () => {
    const req: CreateScrapeJobRequest = {
      route_id: 1,
      travel_date: '2026-05-01'
    }
    expect(typeof req.route_id).toBe('number')
    expect(typeof req.travel_date).toBe('string')
  })
})
