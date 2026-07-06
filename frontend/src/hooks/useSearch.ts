import { useState, useCallback } from 'react'
import { searchApi } from '../api/search'
import { SearchResultItem } from '../types'

interface UseSearchOptions {
  pageSize?: number
  initialQuery?: string
}

export const useSearch = (options: UseSearchOptions = {}) => {
  const { pageSize = 10, initialQuery = '' } = options

  const [query, setQuery] = useState(initialQuery)
  const [results, setResults] = useState<SearchResultItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const [fromCache, setFromCache] = useState(false)

  const search = useCallback(async (searchQuery: string, pageNum: number = 1) => {
    if (!searchQuery.trim()) {
      setResults([])
      setTotal(0)
      return
    }

    setLoading(true)
    setError(null)
    setQuery(searchQuery)
    setPage(pageNum)

    try {
      const response = await searchApi.search(searchQuery, pageSize, pageNum)

      if (pageNum === 1) {
        setResults(response.results)
      } else {
        setResults(prev => [...prev, ...response.results])
      }

      setTotal(response.total)
      setHasMore(response.results.length === pageSize && response.total > pageNum * pageSize)
      setFromCache(response.from_cache || false)

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка поиска')
      if (pageNum === 1) {
        setResults([])
        setTotal(0)
      }
    } finally {
      setLoading(false)
    }
  }, [pageSize])

  const loadMore = useCallback(() => {
    if (!loading && hasMore) {
      search(query, page + 1)
    }
  }, [loading, hasMore, query, page, search])

  const clearResults = useCallback(() => {
    setResults([])
    setTotal(0)
    setQuery('')
    setPage(1)
    setHasMore(false)
    setError(null)
  }, [])

  return {
    query,
    results,
    total,
    loading,
    error,
    page,
    hasMore,
    fromCache,
    search,
    loadMore,
    clearResults,
  }
}