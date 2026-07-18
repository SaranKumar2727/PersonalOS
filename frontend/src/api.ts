export const API_ROOT = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
export const API = `${API_ROOT}/api/v1`
export const FILES = API_ROOT
