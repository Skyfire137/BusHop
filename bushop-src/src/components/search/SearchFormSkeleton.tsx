import { Skeleton } from '@/components/ui/skeleton'

export function SearchFormSkeleton() {
  return (
    <div className="bg-white rounded-card border border-busBorder shadow-card p-4 space-y-3">
      <Skeleton className="h-[52px] w-full rounded-input" />
      <Skeleton className="h-[52px] w-full rounded-input" />
      <Skeleton className="h-[52px] w-full rounded-input" />
      <Skeleton className="h-12 w-full rounded-btn" />
    </div>
  )
}
