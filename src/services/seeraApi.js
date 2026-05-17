const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    })
  } catch {
    throw new Error(
      `Tidak dapat menghubungi server (${API_BASE_URL}). Pastikan backend menyala dan URL di VITE_API_BASE_URL benar.`
    )
  }

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || 'Terjadi kesalahan pada server')
  }

  return response.json()
}

function normalizeSessionId(sessionId) {
  if (sessionId == null || sessionId === '') return null
  const n = Number(sessionId)
  return Number.isFinite(n) && n > 0 ? n : null
}

export function sendChat(payload) {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: payload.message,
      session_id: normalizeSessionId(payload.session_id)
    })
  })
}

export function getRecommendations(payload) {
  const session_id = normalizeSessionId(payload?.session_id)
  if (session_id == null) {
    return Promise.reject(new Error('Session tidak valid. Gunakan Menu Utama lalu profiling ulang.'))
  }
  const top_n = Number(payload?.top_n)
  const body = {
    session_id,
    disable_price: Boolean(payload?.disable_price),
    top_n: Number.isFinite(top_n) && top_n >= 3 && top_n <= 10 ? Math.floor(top_n) : 6
  }
  return request('/recommend', {
    method: 'POST',
    body: JSON.stringify(body)
  })
}

export function getProducts() {
  return request('/products')
}

export function submitFeedback(payload) {
  return request('/feedback', {
    method: 'POST',
    body: JSON.stringify({
      ...payload,
      session_id: normalizeSessionId(payload.session_id)
    })
  })
}

export function getChatHistory(sessionId) {
  return request(`/chat/history/${sessionId}`)
}
