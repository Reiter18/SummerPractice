import { useState, useEffect, useCallback } from 'react'
import { authApi } from '../api/auth'
import { UserResponse } from '../types'

export const useAuth = () => {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const data = await authApi.getMe()
      setUser(data)
      setError(null)
    } catch (err) {
      setError('Не удалось загрузить информацию о пользователе')
      localStorage.removeItem('access_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    try {
      const response = await authApi.login({ username, password })
      localStorage.setItem('access_token', response.access_token)
      await loadUser()
      return { success: true }
    } catch (err: any) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка входа'
      }
    }
  }, [loadUser])

  const register = useCallback(async (username: string, password: string, email?: string) => {
    try {
      await authApi.register({ username, password, email })
      return { success: true }
    } catch (err: any) {
      return {
        success: false,
        error: err.response?.data?.detail || 'Ошибка регистрации'
      }
    }
  }, [])

  const logout = useCallback(() => {
    authApi.logout()
    setUser(null)
    window.location.href = '/login'
  }, [])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  }
}