// Central place for the backend URL. In local development, Vite falls back to
// your localhost backend. Once deployed, set VITE_API_BASE_URL in your hosting
// provider's environment variables to your real backend URL instead.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
