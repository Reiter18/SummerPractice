import { apiClient } from './client'
import { SearchResponse } from '../types'

export const searchApi = {
  search: async (query: string, size: number = 10, page: number = 1): Promise<SearchResponse> => {
    const response = await apiClient.get('/api/v1/search/', {
      params: { q: query, size, page }
    })
    return response.data
  },
}