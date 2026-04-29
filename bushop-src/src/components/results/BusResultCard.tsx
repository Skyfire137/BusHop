'use client'

import { type BusResultCardProps } from '@/types/schedule'

function formatDuration(minutes: number): string {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m > 0 ? `${h}g ${m}p` : `${h}g`
}

function formatPrice(jpy: number): string {
  return `¥${jpy.toLocaleString('ja-JP')}`
}

function buildMapsUrl(pickup_location: string, pickup_lat?: number, pickup_lng?: number): string {
  if (pickup_lat !== undefined && pickup_lng !== undefined) {
    return `https://maps.google.com/maps?q=${pickup_lat},${pickup_lng}`
  }
  return `https://maps.google.com/maps?q=${encodeURIComponent(pickup_location)}`
}

function SeatsDisplay({ seats_available }: { seats_available: number | null }) {
  if (seats_available === null) return null

  if (seats_available === 0) {
    return <span className="text-xs text-red-500 font-medium">Hết ghế</span>
  }

  if (seats_available <= 10) {
    return (
      <span className="text-xs text-busWarning font-medium">
        ⚠ Còn {seats_available} ghế
      </span>
    )
  }

  return <span className="text-xs text-busSuccess font-medium">Còn nhiều ghế</span>
}

export function BusResultCard({
  provider,
  departure_time,
  arrival_time,
  duration_minutes,
  price_jpy,
  seat_type,
  seats_available,
  is_cheapest,
  affiliate_url,
  pickup_location,
  pickup_lat,
  pickup_lng,
}: BusResultCardProps) {
  const mapsUrl = buildMapsUrl(pickup_location, pickup_lat, pickup_lng)

  const cardBorderClass = is_cheapest
    ? 'border-[#F0A0A8]'
    : 'border-busBorder hover:border-busBorderHover'

  return (
    <article
      aria-label={`${provider} ${departure_time}`}
      className={`relative bg-white rounded-card border shadow-card hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-200 p-4 ${cardBorderClass}`}
    >
      {/* Cheapest badge */}
      {is_cheapest && (
        <div className="mb-2">
          <span className="bg-[#FFF0F2] text-busPink border border-[#F8C8D0] rounded-full px-2 py-0.5 text-xs font-medium">
            Rẻ nhất
          </span>
        </div>
      )}

      {/* Main content row */}
      <div className="flex items-start justify-between gap-3">
        {/* Left: Time + Provider */}
        <div className="flex flex-col gap-0.5 min-w-0">
          <div className="text-[24px] font-extrabold text-busTextPrimary leading-tight tracking-tight">
            {departure_time} → {arrival_time}
          </div>
          <div className="text-sm text-busTextSecondary font-medium truncate">
            {provider}
          </div>
        </div>

        {/* Right: Price + Meta */}
        <div className="flex flex-col items-end gap-0.5 shrink-0">
          <span
            aria-label={`Giá vé ${price_jpy} yên`}
            className="text-[26px] font-extrabold text-busPink leading-tight tracking-tight"
          >
            {formatPrice(price_jpy)}
          </span>
          <div className="text-sm text-busTextMuted">
            {seat_type} · {formatDuration(duration_minutes)}
          </div>
        </div>
      </div>

      {/* Seats availability */}
      <div className="mt-1.5">
        <SeatsDisplay seats_available={seats_available} />
      </div>

      {/* Action buttons */}
      <div className="flex items-center gap-2 mt-3">
        <a
          href={mapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`Chỉ đường đến bến ${pickup_location}`}
          className="flex items-center justify-center gap-1.5 border-[1.5px] border-[#E8DDD0] text-busTextSecondary rounded-btn-sm min-h-[44px] px-3 text-sm hover:border-[#C4A080] transition-colors duration-150"
        >
          <span aria-hidden="true">📍</span>
          Chỉ đường bến
        </a>

        <a
          href={affiliate_url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`Xem giá ${provider} giờ ${departure_time}`}
          className="flex items-center justify-center gap-1 bg-busBlue text-white rounded-btn-sm min-h-[44px] px-4 text-sm font-medium hover:bg-busBlueHover transition-colors duration-150 flex-1"
        >
          Xem giá mới nhất →
        </a>
      </div>
    </article>
  )
}
