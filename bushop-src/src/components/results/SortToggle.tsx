'use client'

export type SortOption = 'price' | 'departure' | 'duration'

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: 'price', label: 'Rẻ nhất' },
  { value: 'departure', label: 'Giờ khởi hành' },
  { value: 'duration', label: 'Nhanh nhất' },
]

interface SortToggleProps {
  value: SortOption
  onChange: (sort: SortOption) => void
  className?: string
}

export function SortToggle({ value, onChange, className = '' }: SortToggleProps) {
  return (
    <div
      role="group"
      aria-label="Sắp xếp kết quả"
      className={`flex p-1 bg-[#F0E8D8] rounded-sort gap-1 ${className}`}
    >
      {SORT_OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          aria-pressed={value === option.value}
          data-active={value === option.value}
          onClick={() => onChange(option.value)}
          className={[
            'flex-1 min-h-[44px] px-3 py-2 text-sm rounded-sort-pill transition-all duration-150 font-medium',
            value === option.value
              ? 'bg-white shadow-sm text-busBlue font-bold'
              : 'text-busTextSecondary hover:text-busTextPrimary',
          ].join(' ')}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
