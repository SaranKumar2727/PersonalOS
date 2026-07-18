import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import App from './App'
import { API_ROOT } from './api'

const nativeFetch = window.fetch.bind(window)
window.fetch = (input: RequestInfo | URL, init: RequestInit = {}) => {
  const token = localStorage.getItem('personal-os-token')
  let request: RequestInfo | URL = input
  const raw = String(input)
  if (API_ROOT !== 'http://127.0.0.1:8000' && raw.includes('http://127.0.0.1:8000')) {
    request = raw.replace('http://127.0.0.1:8000', API_ROOT)
  }
  if (!token || !String(request).startsWith(API_ROOT)) return nativeFetch(request, init)
  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${token}`)
  return nativeFetch(request, { ...init, headers })
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
