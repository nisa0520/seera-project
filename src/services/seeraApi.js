const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Terjadi kesalahan pada server')
  }

  return response.json()
}

export function sendChat(payload) {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function getRecommendations(payload) {
  return request('/recommend', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function getProducts() {
  return request('/products')
}
