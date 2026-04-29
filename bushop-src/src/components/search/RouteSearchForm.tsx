'use client'

import { useState, useCallback } from 'react'
import { AutocompleteInput } from './AutocompleteInput'
import { type Prefecture } from '@/lib/prefectures'

interface SearchFormValues {
  origin: Prefecture | null
  destination: Prefecture | null
  date: string
}

interface RouteSearchFormProps {
  onSearch: (values: SearchFormValues) => void
  initialValues?: Partial<SearchFormValues>
  isLoading?: boolean
  className?: string
}

export function RouteSearchForm({
  onSearch,
  initialValues = {},
  isLoading = false,
  className = '',
}: RouteSearchFormProps) {
  const [origin, setOrigin] = useState<Prefecture | null>(initialValues.origin ?? null)
  const [destination, setDestination] = useState<Prefecture | null>(initialValues.destination ?? null)
  const [date, setDate] = useState(initialValues.date ?? '')
  const [touched, setTouched] = useState({ origin: false, destination: false, date: false })

  const canSubmit = Boolean(origin && destination && date)

  const handleSwap = useCallback(() => {
    setOrigin(destination)
    setDestination(origin)
  }, [origin, destination])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!canSubmit || isLoading) return
    onSearch({ origin, destination, date })
  }

  const todayStr = new Date().toISOString().split('T')[0]

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className={`bg-white rounded-card border border-busBorder shadow-card p-4 space-y-3 ${className}`}
    >
      {/* Origin */}
      <div>
        <AutocompleteInput
          label="Điểm đi"
          placeholder="Đi từ đâu?"
          value={origin}
          onChange={(p) => { setOrigin(p); setTouched(t => ({ ...t, origin: true })) }}
        />
        {touched.origin && !origin && (
          <p className="mt-1 text-xs text-busPink">Vui lòng chọn tỉnh/thành phố</p>
        )}
      </div>

      {/* Swap icon */}
      <div className="flex justify-center -my-1">
        <button
          type="button"
          onClick={handleSwap}
          aria-label="Đổi điểm đi và điểm đến"
          className="flex items-center justify-center w-[30px] h-[30px] rounded-full border border-[#E8DDD0] text-busTextMuted hover:border-[#C4A080] transition-colors"
        >
          ⇅
        </button>
      </div>

      {/* Destination */}
      <div>
        <AutocompleteInput
          label="Điểm đến"
          placeholder="Đến đâu?"
          value={destination}
          onChange={(p) => { setDestination(p); setTouched(t => ({ ...t, destination: true })) }}
        />
        {touched.destination && !destination && (
          <p className="mt-1 text-xs text-busPink">Vui lòng chọn tỉnh/thành phố</p>
        )}
      </div>

      {/* Date */}
      <div>
        <label className="block text-sm font-medium text-busTextSecondary mb-1">
          Ngày đi
        </label>
        <input
          type="date"
          min={todayStr}
          value={date}
          onChange={(e) => { setDate(e.target.value); setTouched(t => ({ ...t, date: true })) }}
          onBlur={() => setTouched(t => ({ ...t, date: true }))}
          className="w-full min-h-[44px] px-4 py-3 text-base bg-busCream border-[1.5px] border-[#E8DDD0] rounded-input text-busTextPrimary focus:outline-none focus:ring-2 focus:ring-[#D4607A] focus:border-[#D4607A] transition-colors duration-150"
        />
        {touched.date && !date && (
          <p className="mt-1 text-xs text-busPink">Vui lòng chọn ngày đi</p>
        )}
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!canSubmit || isLoading}
        className="w-full min-h-[44px] bg-busBlue text-white rounded-btn font-medium text-base hover:bg-busBlueHover disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150 flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" aria-hidden="true" />
            <span>Đang tìm...</span>
          </>
        ) : (
          'Tìm vé →'
        )}
      </button>
    </form>
  )
}
