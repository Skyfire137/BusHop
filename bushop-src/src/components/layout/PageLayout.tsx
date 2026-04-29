interface PageLayoutProps {
  children: React.ReactNode
  className?: string
}

export function PageLayout({ children, className = '' }: PageLayoutProps) {
  return (
    <div className={`min-h-screen bg-busCream ${className}`}>
      <main className="max-w-content mx-auto px-4 py-6 sm:py-8">
        {children}
      </main>
    </div>
  )
}
