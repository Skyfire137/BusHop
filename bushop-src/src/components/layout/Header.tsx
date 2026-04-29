'use client'

import Link from 'next/link'
import { useLocale } from 'next-intl'
import { usePathname, useRouter } from 'next/navigation'

const LOCALES = [
  { code: 'vi', label: 'VI' },
  { code: 'en', label: 'EN' },
  { code: 'ja', label: 'JA' },
]

export function Header() {
  const locale = useLocale()
  const pathname = usePathname()
  const router = useRouter()

  function switchLocale(newLocale: string) {
    const segments = pathname.split('/')
    segments[1] = newLocale
    router.push(segments.join('/'))
  }

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-busBorder">
      <div className="max-w-content mx-auto px-4 h-14 sm:h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href={`/${locale}`} className="font-bold text-xl">
          <span className="text-busBlue">Bus</span>
          <span className="text-busPink">Hop</span>
        </Link>

        {/* Lang switcher */}
        <nav aria-label="Chọn ngôn ngữ" className="flex items-center gap-1">
          {LOCALES.map((l) => (
            <button
              key={l.code}
              type="button"
              onClick={() => switchLocale(l.code)}
              aria-current={locale === l.code ? 'true' : undefined}
              className={[
                'min-h-[36px] min-w-[36px] px-3 py-1 text-xs font-medium rounded-sort-pill transition-colors duration-150',
                locale === l.code
                  ? 'bg-busBlue text-white'
                  : 'text-busTextMuted hover:text-busTextSecondary hover:bg-busCream',
              ].join(' ')}
            >
              {l.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}
