import React from 'react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  color?: string
  text?: string
}

const sizeClasses = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'border-indigo-600',
  text,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div
        className={`
          animate-spin rounded-full
          ${sizeClasses[size]}
          ${color}
          border-t-transparent
        `}
      />
      {text && (
        <p className="mt-3 text-sm text-gray-500">{text}</p>
      )}
    </div>
  )
}