import { useState, useEffect, useCallback } from 'react'
import { documentsApi } from '../api/documents'
import { DocumentInfo, UploadFile } from '../types'

export const useDocuments = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState<UploadFile | null>(null)

  const loadDocuments = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await documentsApi.getList()
      setDocuments(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки списка документов')
    } finally {
      setLoading(false)
    }
  }, [])

  const uploadDocument = useCallback(async (file: File, onProgress?: (progress: number) => void) => {
    const uploadFile: UploadFile = {
      id: `${Date.now()}`,
      file,
      name: file.name,
      size: file.size,
      status: 'uploading',
      progress: 0,
    }
    setUploading(uploadFile)

    try {
      const response = await documentsApi.upload(file, (progress) => {
        setUploading(prev => prev ? { ...prev, progress } : null)
        if (onProgress) onProgress(progress)
      })

      setUploading(prev => prev ? { ...prev, status: 'indexing', progress: 50 } : null)

      await new Promise(resolve => setTimeout(resolve, 1000))

      setUploading(prev => prev ? {
        ...prev,
        status: 'done',
        progress: 100,
        documentId: response.document_id,
      } : null)

      await loadDocuments()

      return { success: true, documentId: response.document_id }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Ошибка загрузки документа'
      setUploading(prev => prev ? {
        ...prev,
        status: 'error',
        error: errorMsg,
      } : null)
      return { success: false, error: errorMsg }
    }
  }, [loadDocuments])

  const deleteDocument = useCallback(async (documentId: string) => {
    try {
      await documentsApi.delete(documentId)
      await loadDocuments()
      return { success: true }
    } catch (err: any) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка удаления документа'
      }
    }
  }, [loadDocuments])

  const resetUpload = useCallback(() => {
    setUploading(null)
  }, [])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  return {
    documents,
    loading,
    error,
    uploading,
    uploadDocument,
    deleteDocument,
    resetUpload,
    loadDocuments,
  }
}