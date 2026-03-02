interface LoadingSpinnerProps {
  text?: string
  fullPage?: boolean
}

function LoadingSpinner({ text = 'Loading...', fullPage = false }: LoadingSpinnerProps) {
  const spinner = (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      {text && <p className="text-gray-600 text-sm">{text}</p>}
    </div>
  )

  if (fullPage) {
    return (
      <div className="min-h-[400px] flex items-center justify-center">
        {spinner}
      </div>
    )
  }

  return spinner
}

export default LoadingSpinner
