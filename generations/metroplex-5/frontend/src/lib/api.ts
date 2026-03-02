/**
 * API client for communicating with the FastAPI backend
 */

const API_BASE_URL = '/api'

// Type definitions
export interface User {
  id: string
  name: string
  email: string
  created_at: string
}

export interface Item {
  id: string
  title: string
  description: string | null
  status: 'active' | 'completed' | 'pending'
  user_id: string
  created_at: string
  user?: User
}

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`)
    if (!response.ok) {
      const errorBody = await response.text()
      let errorMessage = `API error: ${response.statusText}`
      try {
        const errorData = JSON.parse(errorBody)
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        errorMessage = errorBody || errorMessage
      }
      throw new Error(errorMessage)
    }
    return response.json()
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      const errorBody = await response.text()
      let errorMessage = `API error: ${response.statusText}`
      try {
        const errorData = JSON.parse(errorBody)
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        errorMessage = errorBody || errorMessage
      }
      throw new Error(errorMessage)
    }
    return response.json()
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      const errorBody = await response.text()
      let errorMessage = `API error: ${response.statusText}`
      try {
        const errorData = JSON.parse(errorBody)
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        errorMessage = errorBody || errorMessage
      }
      throw new Error(errorMessage)
    }
    return response.json()
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      const errorBody = await response.text()
      let errorMessage = `API error: ${response.statusText}`
      try {
        const errorData = JSON.parse(errorBody)
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        errorMessage = errorBody || errorMessage
      }
      throw new Error(errorMessage)
    }
    return response.json()
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.get('/health')
  }
}

export const apiClient = new ApiClient()
