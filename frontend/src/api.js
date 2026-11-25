import Cookies from 'js-cookie'

export const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
export const apiUrl = path => `${BASE_URL}${path}`

const ACCESS_TOKEN_KEY = 'jwt_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export const getAccessToken = () => Cookies.get(ACCESS_TOKEN_KEY)
export const getRefreshToken = () => Cookies.get(REFRESH_TOKEN_KEY)
export const saveTokens = ({ access, refresh }) => {
  Cookies.set(ACCESS_TOKEN_KEY, access, { expires: 30 })
  Cookies.set(REFRESH_TOKEN_KEY, refresh, { expires: 30 })
}
export const clearTokens = () => {
  Cookies.remove(ACCESS_TOKEN_KEY)
  Cookies.remove(REFRESH_TOKEN_KEY)
}

export const apiFetch = async (path, options = {}) => {
  const send = async () => {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
    const token = getAccessToken()
    if (token) headers.Authorization = `Bearer ${token}`
    const response = await fetch(apiUrl(path), { ...options, headers })
    const text = await response.text()
    let data = null
    if (text) {
      try { data = JSON.parse(text) } catch { data = { detail: text } }
    }
    return { ok: response.ok, status: response.status, data }
  }

  let result = await send()
  if (result.status === 401 && path !== '/api/users/login/' && path !== '/api/users/register/') {
    const refresh = getRefreshToken()
    if (refresh) {
      const refreshResponse = await fetch(apiUrl('/api/users/refresh/'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      })
      if (refreshResponse.ok) {
        const refreshed = await refreshResponse.json()
        saveTokens({ access: refreshed.access, refresh })
        result = await send()
      }
    }
    if (result.status === 401) {
      clearTokens()
      result = await send()
    }
  }
  return result
}
