// Auth
export interface UserLogin {
  username: string
  password: string
}

export interface UserRegister {
  username: string
  password: string
  email?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  username: string
  email?: string
  created_at: string
  is_active: boolean
}

// Documents
export interface DocumentUploadResponse {
  document_id: string
  file_name: string
  file_size: number
  chunks_indexed: number
  status: string
  message?: string
}

export interface DocumentInfo {
  document_id: string
  file_name: string
  uploaded_at: string
  chunks_count: number
  file_size: number
  status: string
}

// Search
export interface SearchResultItem {
  chunk_id: string
  document_id: string
  file_name: string
  page: number
  text: string
  score: number
}

export interface SearchResponse {
  query: string
  total: number
  results: SearchResultItem[]
  from_cache: boolean
}

// Upload
export interface UploadFile {
  id: string
  file: File
  name: string
  size: number
  status: 'uploading' | 'indexing' | 'done' | 'error'
  progress: number
  documentId?: string
  error?: string
}

// Pagination
export interface PaginationParams {
  page: number
  size: number
  total?: number
}