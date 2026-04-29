'use client'

import { useState, useRef, useEffect, useCallback, useId } from 'react'
import { Prefecture, searchPrefectures } from '@/lib/prefectures'

interface AutocompleteInputProps {
  id?: string
  label: string
  placeholder: string
  value: Prefecture | null
  onChange: (prefecture: Prefecture | null) => void
  className?: string
}

export function AutocompleteInput({
  id,
  label,
  placeholder,
  value,
  onChange,
  className = '',
}: AutocompleteInputProps) {
  const [inputValue, setInputValue] = useState(value?.name_vi ?? '')
  const [suggestions, setSuggestions] = useState<Prefecture[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)

  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLUListElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // useId must be called unconditionally — we always generate a fallback id
  const generatedId = useId()
  const listboxId = useId()
  const inputId = id ?? generatedId

  // Sync when value changes externally
  useEffect(() => {
    setInputValue(value?.name_vi ?? '')
  }, [value])

  // Cleanup debounce timer on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [])

  const search = useCallback((q: string) => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      const results = searchPrefectures(q)
      setSuggestions(results)
      setIsOpen(results.length > 0)
      setActiveIndex(-1)
    }, 150)
  }, [])

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const q = e.target.value
    setInputValue(q)
    if (q.length === 0) {
      onChange(null)
      setSuggestions([])
      setIsOpen(false)
    } else {
      search(q)
    }
  }

  function handleSelect(prefecture: Prefecture) {
    setInputValue(prefecture.name_vi)
    setSuggestions([])
    setIsOpen(false)
    setActiveIndex(-1)
    onChange(prefecture)
    inputRef.current?.blur()
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!isOpen) return
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setActiveIndex((i) => Math.min(i + 1, suggestions.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setActiveIndex((i) => Math.max(i - 1, 0))
        break
      case 'Enter':
        e.preventDefault()
        if (activeIndex >= 0 && suggestions[activeIndex]) {
          handleSelect(suggestions[activeIndex])
        }
        break
      case 'Escape':
        setIsOpen(false)
        setActiveIndex(-1)
        break
    }
  }

  // Scroll active item into view
  useEffect(() => {
    if (activeIndex >= 0 && listRef.current) {
      const item = listRef.current.children[activeIndex] as HTMLElement | undefined
      item?.scrollIntoView({ block: 'nearest' })
    }
  }, [activeIndex])

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        inputRef.current &&
        !inputRef.current.closest('[data-autocomplete]')?.contains(e.target as Node)
      ) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const activeOptionId = activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined

  return (
    <div data-autocomplete className={`relative ${className}`}>
      <label
        htmlFor={inputId}
        className="block text-sm font-medium text-busTextSecondary mb-1"
      >
        {label}
      </label>

      <input
        ref={inputRef}
        id={inputId}
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoComplete="off"
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={isOpen}
        aria-controls={listboxId}
        aria-activedescendant={activeOptionId}
        className={[
          'w-full min-h-[44px] px-4 py-3 text-base',
          'bg-busCream border-[1.5px] border-[#E8DDD0] rounded-input',
          'text-busTextPrimary placeholder:text-busTextPlaceholder',
          'focus:outline-none focus:ring-2 focus:ring-[#D4607A] focus:border-[#D4607A]',
          'transition-colors duration-150',
        ].join(' ')}
      />

      {isOpen && suggestions.length > 0 && (
        <ul
          ref={listRef}
          id={listboxId}
          role="listbox"
          aria-label={label}
          className={[
            'absolute z-50 w-full mt-1',
            'bg-white border border-busBorder rounded-card shadow-card',
            'max-h-[240px] overflow-y-auto',
          ].join(' ')}
        >
          {suggestions.map((prefecture, index) => (
            <li
              key={prefecture.id}
              id={`${listboxId}-option-${index}`}
              role="option"
              aria-selected={index === activeIndex}
              onMouseDown={(e) => {
                // preventDefault keeps input focused until we explicitly blur after selection
                e.preventDefault()
                handleSelect(prefecture)
              }}
              onMouseEnter={() => setActiveIndex(index)}
              className={[
                'flex items-center justify-between px-4 py-3 cursor-pointer min-h-[44px]',
                'text-busTextPrimary text-base',
                index === activeIndex
                  ? 'bg-busCream text-busBlue font-medium'
                  : 'hover:bg-[#FFF8F0]',
              ].join(' ')}
            >
              <span>{prefecture.name_vi}</span>
              <span className="text-sm text-busTextMuted">{prefecture.name_ja}</span>
            </li>
          ))}
        </ul>
      )}

      {isOpen && suggestions.length === 0 && inputValue.length > 0 && (
        <div
          role="status"
          aria-live="polite"
          className="absolute z-50 w-full mt-1 bg-white border border-busBorder rounded-card shadow-card px-4 py-3 text-busTextMuted text-sm"
        >
          Không tìm thấy &ldquo;{inputValue}&rdquo;
        </div>
      )}
    </div>
  )
}
