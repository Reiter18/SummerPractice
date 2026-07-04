import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Login } from './components/auth/Login'
import { Register } from './components/auth/Register'
import { Header } from './components/common/Header'
import { Footer } from './components/common/Footer'
import { LoadingSpinner } from './components/common/LoadingSpinner'
import { UploadArea } from './components/documents/UploadArea'
import { UploadProgress } from './components/documents/UploadProgress'
import { DocumentList } from './components/documents/DocumentList'
import { SearchBar } from './components/search/SearchBar'
import { SearchResults } from './components/search/SearchResults'
import { useAuth } from './hooks/useAuth'
import { useDocuments } from './hooks/useDocuments'
import { useSearch } from './hooks/useSearch'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

const HomePage: React.FC = () => {
  const { user, loading: authLoading } = useAuth()
  const {
    uploading,
    uploadDocument,
    resetUpload,
    loadDocuments
  } = useDocuments()
  const {
    query,
    results,
    total,
    loading: searchLoading,
    hasMore,
    fromCache,
    search,
    loadMore,
  } = useSearch({ pageSize: 10 })

  const handleFileUpload = async (file: File) => {
    const result = await uploadDocument(file)
    if (result.success) {
      await loadDocuments()
    }
  }

  const handleDocumentDeleted = () => {
    loadDocuments()
  }

  if (authLoading) {
    return <LoadingSpinner text="Загрузка..." />
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header username={user?.username} />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          {/* Левая колонка - Загрузка документов */}
          <div className="lg:col-span-1 space-y-4 sm:space-y-6 order-2 lg:order-1">
            <div className="bg-white rounded-lg shadow p-4 sm:p-6">
              <h2 className="text-base sm:text-lg font-medium text-gray-700 mb-4">
                Загрузка документа
              </h2>
              <UploadArea
                onFileAccepted={handleFileUpload}
                disabled={!!uploading && uploading.status !== 'done' && uploading.status !== 'error'}
              />

              {uploading && (
                <div className="mt-4">
                  <UploadProgress
                    fileName={uploading.name}
                    fileSize={uploading.size}
                    status={uploading.status}
                    progress={uploading.progress}
                    error={uploading.error}
                  />
                  {(uploading.status === 'done' || uploading.status === 'error') && (
                    <button
                      onClick={() => {
                        resetUpload()
                        if (uploading.status === 'done') {
                          loadDocuments()
                        }
                      }}
                      className="mt-2 text-sm text-indigo-600 hover:text-indigo-800"
                    >
                      {uploading.status === 'done' ? 'Загрузить ещё' : 'Попробовать снова'}
                    </button>
                  )}
                </div>
              )}
            </div>

            <DocumentList onDocumentDeleted={handleDocumentDeleted} />
          </div>

          {/* Правая колонка - Поиск */}
          <div className="lg:col-span-2 space-y-4 sm:space-y-6 order-1 lg:order-2">
            <div className="bg-white rounded-lg shadow p-4 sm:p-6">
              <SearchBar onSearch={search} loading={searchLoading} />
              {fromCache && (
                <p className="text-xs text-gray-400 mt-2 text-center">
                  Результат из кеша
                </p>
              )}
            </div>

            {(query || searchLoading) && (
              <div className="bg-white rounded-lg shadow p-4 sm:p-6">
                <SearchResults
                  results={results}
                  query={query}
                  total={total}
                  loading={searchLoading}
                  onLoadMore={loadMore}
                  hasMore={hasMore}
                  pageSize={10}
                />
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App