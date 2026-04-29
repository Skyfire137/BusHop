import { Skeleton } from '@/components/ui/skeleton'

export function ResultCardSkeleton() {
  return (
    <div className="bg-white rounded-card border border-busBorder shadow-card p-4 space-y-3">
      {/* badge area */}
      <Skeleton className="h-5 w-16 rounded-full" />
      {/* time + price row */}
      <div className="flex justify-between items-center">
        <Skeleton className="h-8 w-28" />
        <Skeleton className="h-8 w-20" />
      </div>
      {/* provider + meta row */}
      <div className="flex justify-between items-center">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-24" />
      </div>
      {/* buttons row */}
      <div className="flex gap-2 pt-1">
        <Skeleton className="h-11 flex-1 rounded-btn-sm" />
        <Skeleton className="h-11 flex-1 rounded-btn-sm" />
      </div>
    </div>
  )
}

export function ResultListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <ResultCardSkeleton key={i} />
      ))}
    </div>
  )
}
