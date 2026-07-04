import React from 'react'
import { formatFileSize } from '../../utils/helpers'

interface UploadProgressProps {
  fileName: string
  fileSize: number
  status: 'uploading' | 'indexing' | 'done' | 'error'
  progress: number
  error?: string
}

const statusLabels = {
  uploading: 'Загрузка...',
  indexing: 'Индексация...',
  done: 'Готово',
  error: 'Ошибка',
}

const statusColors = {
  uploading: 'bg-blue-500',
  indexing: 'bg-yellow-500',
  done: 'bg-green-500',
  error: 'bg-red-500',
}

export const UploadProgress: React.FC<UploadProgressProps> = ({
  fileName,
  fileSize,
  status,
  progress,
  error,
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-2">
        <span className="font-medium text-gray-700 truncate flex-1 w-full">
          {fileName}
        </span>
        <span className={`text-sm font-medium whitespace-nowrap ${
          status === 'done' ? 'text-green-600' :
          status === 'error' ? 'text-red-600' :
          'text-gray-600'
        }`}>
          {statusLabels[status]}
        </span>
      </div>

      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{formatFileSize(fileSize)}</span>
        <span>{Math.min(progress, 100)}%</span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${statusColors[status]}`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>

      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}
    </div>
  )
}