import React, { useEffect, useState } from 'react'
import { documentsApi } from '../../api/documents'
import { DocumentInfo } from '../../types'
import { formatDate, formatFileSize, getStatusColor, getStatusLabel } from '../../utils/helpers'

interface DocumentListProps {
  onDocumentDeleted?: () => void
}

export const DocumentList: React.FC<DocumentListProps> = ({ onDocumentDeleted }) => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<string | null>(null)

  const loadDocuments = async () => {
    try {
      const data = await documentsApi.getList()
      setDocuments(data)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  const handleDelete = async (documentId: string) => {
    if (!confirm('Вы уверены, что хотите удалить этот документ?')) return

    setDeleting(documentId)
    try {
      await documentsApi.delete(documentId)
      await loadDocuments()
      if (onDocumentDeleted) onDocumentDeleted()
    } catch (error) {
      console.error('Failed to delete document:', error)
      alert('Ошибка при удалении документа')
    } finally {
      setDeleting(null)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-8 text-gray-500">
        Загрузка документов...
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        Нет загруженных документов
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-700">
        Загруженные документы ({documents.length})
      </h3>

      {/* Десктопная таблица */}
      <div className="hidden md:block overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Название
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Дата
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Размер
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {documents.map((doc) => (
              <tr key={doc.document_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900 truncate max-w-xs">
                  {doc.file_name}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                  {formatDate(doc.uploaded_at)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                  {formatFileSize(doc.file_size)}
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className={`inline-flex px-2 py-1 text-xs rounded-full ${getStatusColor(doc.status)}`}>
                    {getStatusLabel(doc.status)}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  <button
                    onClick={() => handleDelete(doc.document_id)}
                    disabled={deleting === doc.document_id}
                    className="text-red-600 hover:text-red-800 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {deleting === doc.document_id ? 'Удаление...' : '🗑 Удалить'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Мобильные карточки с кнопкой удаления */}
      <div className="md:hidden space-y-3">
        {documents.map((doc) => (
          <div key={doc.document_id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-start">
              <span className="font-medium text-gray-900 text-sm truncate flex-1">
                {doc.file_name}
              </span>
              <span className={`ml-2 px-2 py-1 text-xs rounded-full whitespace-nowrap ${getStatusColor(doc.status)}`}>
                {getStatusLabel(doc.status)}
              </span>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-1 text-xs text-gray-500">
              <span>{formatDate(doc.uploaded_at)}</span>
              <span>{formatFileSize(doc.file_size)}</span>
            </div>
            <button
              onClick={() => handleDelete(doc.document_id)}
              disabled={deleting === doc.document_id}
              className="mt-2 text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
            >
              {deleting === doc.document_id ? 'Удаление...' : '🗑 Удалить'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}