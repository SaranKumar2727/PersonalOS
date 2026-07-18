import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import App from './App'

const nativeFetch = window.fetch.bind(window)
window.fetch = (input: RequestInfo | URL, init: RequestInit = {}) => {
  const token = localStorage.getItem('personal-os-token')
  if (!token || !String(input).includes('127.0.0.1:8000')) return nativeFetch(input, init)
  const headers = new Headers(init.headers)
  headers.set('Authorization', `Bearer ${token}`)
  return nativeFetch(input, {...init, headers})
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
