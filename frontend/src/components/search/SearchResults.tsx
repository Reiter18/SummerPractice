import React, { useState } from 'react'
import { SearchResultItem } from '../../types'
import { HighlightText } from './HighlightText'

interface SearchResultsProps {
  results: SearchResultItem[]
  query: string
  total: number
  loading?: boolean
  onLoadMore?: () => void
  hasMore?: boolean
  pageSize?: number
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  query,
  total,
  loading,
  onLoadMore,
  hasMore = false,
  pageSize = 10,
}) => {
  const [showAll, setShowAll] = useState(false)

  if (loading) {
    return (
      <div className="text-center py-12 text-gray-500">
        Поиск...
      </div>
    )
  }

  if (total === 0) {
    return (
      <div className="text-center py-12 px-4">
        <p className="text-gray-500 text-lg">
          По вашему запросу ничего не найдено.
        </p>
        <p className="text-gray-400 text-sm mt-2">
          Попробуйте изменить формулировку
        </p>
      </div>
    )
  }

  const displayResults = showAll ? results : results.slice(0, pageSize)
  const hasMoreResults = results.length > pageSize && !showAll

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <p className="text-sm text-gray-500">
          Найдено: {total} результатов
          {results.length < total && ` (показано ${results.length})`}
        </p>
        <p className="text-xs text-gray-400">
          {showAll ? 'Показаны все результаты' : `Показаны первые ${Math.min(pageSize, results.length)}`}
        </p>
      </div>

      {/* Результаты в виде карточек */}
      {displayResults.map((result) => (
        <div
          key={result.chunk_id}
          className="bg-white rounded-lg shadow p-4 sm:p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-2">
            <h4 className="text-base sm:text-lg font-medium text-indigo-600 truncate max-w-full sm:max-w-xs md:max-w-md">
              {result.file_name}
            </h4>
            <span className="text-xs sm:text-sm text-gray-400 bg-gray-100 px-2 py-1 rounded whitespace-nowrap">
              Страница {result.page}
            </span>
          </div>

          <p className="text-sm sm:text-base text-gray-700 mb-3 leading-relaxed">
            <HighlightText text={result.text} query={query} />
          </p>

          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1 text-xs sm:text-sm text-gray-400">
            <span>Релевантность: {result.score.toFixed(2)}</span>
            <span className="text-xs">ID: {result.chunk_id.slice(0, 8)}...</span>
          </div>
        </div>
      ))}

      {/* Кнопка "Загрузить ещё" или "Показать все" */}
      {(hasMoreResults || hasMore) && (
        <div className="text-center pt-4">
          {onLoadMore ? (
            <button
              onClick={onLoadMore}
              disabled={loading}
              className="px-6 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Загрузка...' : 'Загрузить ещё 10'}
            </button>
          ) : (
            <button
              onClick={() => setShowAll(true)}
              className="px-6 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors"
            >
              Показать все ({results.length})
            </button>
          )}
        </div>
      )}
    </div>
  )
}