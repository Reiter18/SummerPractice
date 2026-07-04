import { apiClient } from './client'
import { DocumentUploadResponse, DocumentInfo } from '../types'

export const documentsApi = {
  upload: async (file: File, onProgress?: (progress: number) => void): Promise<DocumentUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      },
    })
    return response.data
  },

  getList: async (): Promise<DocumentInfo[]> => {
    const response = await apiClient.get('/api/v1/documents/')
    return response.data
  },

  delete: async (documentId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/documents/${documentId}`)
  },
}