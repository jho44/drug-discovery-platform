interface ErrorBannerProps {
  message: string
}

export function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className="rounded-md bg-red-50 border border-red-200 px-4 py-3 text-red-700 text-sm">
      <span className="font-medium">Error: </span>
      {message}
    </div>
  )
}
