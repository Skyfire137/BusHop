'use client'

type EmptyStateVariant = 'no-results' | 'error' | 'loading'

interface EmptyStateProps {
  variant: EmptyStateVariant
  onRetry?: () => void
  providerUrl?: string
  className?: string
}

function SkeletonCard() {
  return (
    <div className="animate-pulse bg-white rounded-card border border-busBorder shadow-card p-4">
      <div className="h-4 bg-[#F0E8D8] rounded w-1/3 mb-3" />
      <div className="flex justify-between">
        <div className="h-8 bg-[#F0E8D8] rounded w-1/3" />
        <div className="h-8 bg-[#F0E8D8] rounded w-1/4" />
      </div>
      <div className="h-4 bg-[#F0E8D8] rounded w-1/2 mt-3" />
      <div className="flex gap-2 mt-4">
        <div className="h-10 bg-[#F0E8D8] rounded-btn-sm flex-1" />
        <div className="h-10 bg-[#F0E8D8] rounded-btn flex-1" />
      </div>
    </div>
  )
}

export function EmptyState({ variant, onRetry, providerUrl, className = '' }: EmptyStateProps) {
  if (variant === 'no-results') {
    return (
      <div className={`flex flex-col items-center text-center py-12 px-4 ${className}`}>
        <span aria-hidden="true" className="text-4xl mb-3">🚌</span>
        <h2 className="text-lg font-semibold text-busTextPrimary">Không có chuyến xe</h2>
        <p className="text-sm text-busTextMuted mt-1">
          Chúng tôi không tìm thấy chuyến nào cho tuyến này.
        </p>
        <button
          type="button"
          className="mt-4 bg-busBlue text-white rounded-btn min-h-[44px] px-6 text-sm font-medium hover:bg-busBlueHover transition-colors duration-150"
        >
          Thử tuyến khác
        </button>
      </div>
    )
  }

  if (variant === 'error') {
    return (
      <div className={`flex flex-col items-center text-center py-12 px-4 ${className}`}>
        <span aria-hidden="true" className="text-4xl mb-3">⚠️</span>
        <h2 className="text-lg font-semibold text-busTextPrimary">Hệ thống đang bận</h2>
        <p className="text-sm text-busTextMuted mt-1">
          Không thể tải dữ liệu. Vui lòng thử lại.
        </p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 bg-busBlue text-white rounded-btn min-h-[44px] px-6 text-sm font-medium hover:bg-busBlueHover transition-colors duration-150"
          >
            Thử lại
          </button>
        )}
        {providerUrl && (
          <a
            href={providerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 text-busBlue text-sm underline"
          >
            Xem trực tiếp tại nhà xe
          </a>
        )}
      </div>
    )
  }

  // variant === 'loading'
  return (
    <div
      role="status"
      aria-live="polite"
      className={`py-12 px-4 ${className}`}
    >
      <div className="flex flex-col gap-3">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <div className="text-center mt-6">
        <p className="text-lg font-semibold text-busTextPrimary">Đang tìm vé cho bạn...</p>
        <p className="text-sm text-busTextMuted mt-1">
          Có thể mất 30-60 giây, vui lòng chờ.
        </p>
      </div>
    </div>
  )
}
