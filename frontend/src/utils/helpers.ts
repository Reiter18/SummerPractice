export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const truncateText = (text: string, maxLength: number = 200): string => {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    indexed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    processing: 'bg-yellow-100 text-yellow-800',
    done: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

export const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    indexed: 'Индексирован',
    failed: 'Ошибка',
    processing: 'Обработка',
    done: 'Готово',
    error: 'Ошибка',
  }
  return labels[status] || status
}