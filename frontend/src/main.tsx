import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import App from './App'
import { API_ROOT } from './api'

const nativeFetch = window.fetch.bind(window)
window.fetch = async (input: RequestInfo | URL, init: RequestInit = {}) => {
  const token = localStorage.getItem('personal-os-token')
  let request: RequestInfo | URL = input
  const raw = String(input)
  if (API_ROOT !== 'http://127.0.0.1:8000' && raw.includes('http://127.0.0.1:8000')) {
    request = raw.replace('http://127.0.0.1:8000', API_ROOT)
  }
  if (!token || !String(request).startsWith(API_ROOT)) return nativeFetch(request, init)
  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${token}`)
  const response = await nativeFetch(request, { ...init, headers })
  const method = (init.method || 'GET').toUpperCase()
  if (response.ok && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && !String(request).includes('/ai/')) {
    const message = method === 'DELETE'
      ? 'Deleted successfully'
      : String(request).includes('/settings/') || method !== 'POST'
        ? 'Saved successfully'
        : 'Added successfully'
    window.dispatchEvent(new CustomEvent('personal-os:notify', { detail: message }))
  }
  return response
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
