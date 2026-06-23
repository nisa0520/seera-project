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
  // FormData: biarkan browser yang menentukan Content-Type (multipart boundary)
  const isFormData = options.body instanceof FormData
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options.headers || {})
  }
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
  apiBase: API_BASE,
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
  },
  // ── Image-based skin detection & visual matching ──
  setInputMethod(sessionId, method) {
    return request(`/api/v1/conversations/${sessionId}/input-method`, {
      method: 'POST',
      body: JSON.stringify({ method })
    })
  },
  startImageMode(sessionId) {
    return request(`/api/v1/conversations/${sessionId}/image-mode`, {
      method: 'POST'
    })
  },
  analyzeImage(sessionId, file, sourceType = 'UPLOAD') {
    const form = new FormData()
    form.append('image_file', file, file.name || 'wajah.jpg')
    form.append('source_type', sourceType)
    return request(`/api/v1/conversations/${sessionId}/image-analysis`, {
      method: 'POST',
      body: form
    })
  },
  confirmImageAnalysis(sessionId, { isConfirmed, correctedSkinTone = null, correctedUndertone = null }) {
    return request(`/api/v1/conversations/${sessionId}/image-analysis/confirm`, {
      method: 'POST',
      body: JSON.stringify({
        is_confirmed: isConfirmed,
        corrected_skin_tone: correctedSkinTone,
        corrected_undertone: correctedUndertone
      })
    })
  },
  listBackgrounds() {
    return request('/api/v1/backgrounds')
  },
  createVisualMatch(sessionId, { recommendationId = null, productId, backgroundId = null }) {
    return request(`/api/v1/conversations/${sessionId}/visual-match`, {
      method: 'POST',
      body: JSON.stringify({
        recommendation_id: recommendationId,
        product_id: productId,
        background_id: backgroundId
      })
    })
  },
  // ── Realistic Virtual Try-On (IDM-VTON, asset-tier aware) ──
  uploadVtonPersonImage(sessionId, file, sourceType = 'UPLOAD', consentConfirmed = false) {
    const form = new FormData()
    form.append('image_file', file, file.name || 'badan.jpg')
    form.append('source_type', sourceType)
    form.append('consent_confirmed', consentConfirmed ? 'true' : 'false')
    return request(`/api/v1/conversations/${sessionId}/vton/person-image`, {
      method: 'POST',
      body: form
    })
  },
  createVtonJob(
    sessionId,
    { productId, personImageId, backgroundId = null, variantId = null, confirmExperimental = false }
  ) {
    return request(`/api/v1/conversations/${sessionId}/vton/jobs`, {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        person_image_id: personImageId,
        background_id: backgroundId,
        variant_id: variantId,
        confirm_experimental: confirmExperimental
      })
    })
  },
  vtonEligibility(productId, variantId = null) {
    const qs = variantId != null ? `?variant_id=${variantId}` : ''
    return request(`/api/v1/products/${productId}/vton-eligibility${qs}`)
  },
  getVtonJob(jobId) {
    return request(`/api/v1/vton/jobs/${jobId}`)
  },
  submitVtonFeedback(jobId, ratings) {
    return request(`/api/v1/vton/jobs/${jobId}/feedback`, {
      method: 'POST',
      body: JSON.stringify(ratings)
    })
  }
}
