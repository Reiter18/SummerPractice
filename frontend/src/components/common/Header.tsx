import React from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../../api/auth'

interface HeaderProps {
  username?: string
}

export const Header: React.FC<HeaderProps> = ({ username }) => {
  const navigate = useNavigate()

  const handleLogout = () => {
    authApi.logout()
    navigate('/login')
  }

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔍</span>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
              Поиск по базе знаний
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {username && (
              <span className="text-sm text-gray-600 hidden sm:inline">
                {username}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Выйти
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}