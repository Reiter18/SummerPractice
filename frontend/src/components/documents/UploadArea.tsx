import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface UploadAreaProps {
  onFileAccepted: (file: File) => void
  disabled?: boolean
}

export const UploadArea: React.FC<UploadAreaProps> = ({ onFileAccepted, disabled }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0 && !disabled) {
      onFileAccepted(acceptedFiles[0])
    }
  }, [onFileAccepted, disabled])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 20 * 1024 * 1024,
    disabled,
    multiple: false,
  })

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        <div className="space-y-2">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="text-gray-600">
            {isDragActive ? 'Отпустите файл для загрузки' : 'Перетащите файл сюда или кликните для выбора'}
          </p>
          <p className="text-sm text-gray-400">
            Поддерживаются: PDF, DOCX (макс. 20 МБ)
          </p>
        </div>
      </div>

      {fileRejections.length > 0 && (
        <div className="text-red-600 text-sm">
          {fileRejections.map((rejection) => (
            <p key={rejection.file.name}>
              {rejection.file.name}: {rejection.errors.map(e => e.message).join(', ')}
            </p>
          ))}
        </div>
      )}
    </div>
  )
}