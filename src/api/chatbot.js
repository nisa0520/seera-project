const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function fingerprint() {
  const KEY = 'seera_fingerprint'
  let fp = localStorage.getItem(KEY)
  if (!fp) {
    fp = 'seera-' + Math.random().toString(36).slice(2) + Date.now().toString(36)
    localStorage.setItem(KEY, fp)
  }
  return fp
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const text = await response.text()
  let payload
  try {
    payload = text ? JSON.parse(text) : null
  } catch {
    payload = { raw: text }
  }
  if (!response.ok) {
    const err = new Error('API error')
    err.status = response.status
    err.body = payload
    throw err
  }
  return payload
}

export const chatbotApi = {
  start() {
    return request('/api/v1/conversations/start', {
      method: 'POST',
      body: JSON.stringify({ user_fingerprint: fingerprint() })
    })
  },
  setGender(sessionId, gender) {
  return request(`/api/v1/conversations/${sessionId}/gender`, {
    method: 'POST',
    body: JSON.stringify({ gender })
  })
},
  setSkinTone(sessionId, skinTone) {
    return request(`/api/v1/conversations/${sessionId}/skin-tone`, {
      method: 'POST',
      body: JSON.stringify({ skin_tone: skinTone })
    })
  },
  setUndertone(sessionId, undertone) {
    return request(`/api/v1/conversations/${sessionId}/undertone`, {
      method: 'POST',
      body: JSON.stringify({ undertone })
    })
  },
  confirm(sessionId, { isConfirmed, changeTarget = null, topN = 5 }) {
    return request(`/api/v1/conversations/${sessionId}/confirm`, {
      method: 'POST',
      body: JSON.stringify({
        is_confirmed: isConfirmed,
        change_target: changeTarget,
        top_n: topN
      })
    })
  },
  filter(sessionId, criteria) {
    return request(`/api/v1/conversations/${sessionId}/recommendations/filter`, {
      method: 'POST',
      body: JSON.stringify({ criteria })
    })
  },
  colorsToAvoid(sessionId) {
    return request(`/api/v1/conversations/${sessionId}/colors-to-avoid`)
  },
  freeText(sessionId, message) {
    return request(`/api/v1/conversations/${sessionId}/free-text`, {
      method: 'POST',
      body: JSON.stringify({ message })
    })
  },
  listEducationTopics(sessionId = null) {
    const qs = sessionId ? `?session_id=${sessionId}` : ''
    return request(`/api/v1/education/topics${qs}`)
  },
  getEducationTopic(code, sessionId = null) {
    const qs = sessionId ? `?session_id=${sessionId}` : ''
    return request(`/api/v1/education/topics/${code}${qs}`)
  },
  submitFeedback(sessionId, payload) {
    return request(`/api/v1/conversations/${sessionId}/feedback`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  }
}
