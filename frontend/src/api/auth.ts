import { apiClient } from './client'
import { UserLogin, UserRegister, TokenResponse, UserResponse } from '../types'

export const authApi = {
  login: async (data: UserLogin): Promise<TokenResponse> => {
    const response = await apiClient.post('/api/v1/auth/login', data)
    return response.data
  },

  register: async (data: UserRegister): Promise<UserResponse> => {
    const response = await apiClient.post('/api/v1/auth/register', data)
    return response.data
  },

  getMe: async (): Promise<UserResponse> => {
    const response = await apiClient.get('/api/v1/auth/me')
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
  },
}