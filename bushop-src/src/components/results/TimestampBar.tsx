interface TimestampBarProps {
  scraped_at: string
  className?: string
}

function getDataStatus(scraped_at: string): 'fresh' | 'stale' | 'hidden' {
  const now = Date.now()
  const scrapedMs = new Date(scraped_at).getTime()
  const ageMs = now - scrapedMs
  const HOUR = 60 * 60 * 1000
  if (ageMs < 6 * HOUR) return 'fresh'
  if (ageMs < 24 * HOUR) return 'stale'
  return 'hidden'
}

function formatTime(isoString: string): string {
  return new Date(isoString).toLocaleTimeString('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Tokyo',
  })
}

export function TimestampBar({ scraped_at, className = '' }: TimestampBarProps) {
  const status = getDataStatus(scraped_at)
  if (status === 'hidden') return null

  return (
    <div className={`flex items-center gap-2 text-xs text-busTextMuted ${className}`}>
      <span>Cập nhật lúc {formatTime(scraped_at)}</span>
      {status === 'stale' && (
        <span className="bg-[#FEF3EC] text-[#F57C3A] border border-[#F8D5B8] rounded-full px-2 py-0.5 text-xs font-medium">
          Dữ liệu cũ
        </span>
      )}
    </div>
  )
}
