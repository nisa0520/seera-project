<template>
  <!-- Floating Bubble Button -->
  <button
    v-if="!isOpen"
    @click="openChat"
    class="chatbot-bubble-btn"
    aria-label="Buka Seera Assistant"
  >
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  </button>

  <!-- Chat Panel Overlay -->
  <Transition name="chat-panel">
    <div v-if="isOpen" class="seera-chat-widget">
      <!-- Header -->
      <div class="chat-head">
        <div class="chat-head-left">
          <div class="avatar"></div>
          <div>
            <div class="chat-head-name">Seera</div>
            <div class="chat-head-status">● Online · personal color stylist</div>
          </div>
        </div>
        <div class="chat-head-actions">
          <button @click="resetSession" class="icon-btn" title="Reset sesi">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>
            </svg>
          </button>
          <button @click="closeChat" class="icon-btn" title="Tutup">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div class="messages" ref="messagesContainer">
        <div class="messages-inner">
          <div class="day-divider">Hari ini · {{ new Date().toLocaleDateString("id-ID", {day:"numeric", month:"long"}) }}</div>
          
          <div v-for="(msg, idx) in messages" :key="idx" :class="['msg-row', msg.role === 'user' ? 'user' : '']">
            <div v-if="msg.role === 'bot'" class="msg-avatar"></div>

            <div class="msg-stack">
              <!-- Multimodal -->
              <div v-if="msg.blocks" class="multimodal-blocks">
                <div v-for="(block, bIdx) in msg.blocks" :key="bIdx" class="block-item">
                  <template v-if="block.type === 'text'">
                    <div class="bubble" v-html="formatMessage(block.content)"></div>
                  </template>

                  <!-- Interactive Fitzpatrick -->
                  <template v-else-if="block.type === 'image' && block.alt && block.alt.includes('Fitzpatrick')">
                    <div class="block">
                      <div class="block-head" style="padding: 14px 14px 0;">
                        <div>
                          <div class="block-tag">FITZPATRICK SCALE · I–VI</div>
                          <div class="block-title">Mana yang paling mirip kulitmu?</div>
                        </div>
                      </div>
                      <div class="fitz fitz-grid-wrap">
                        <div v-for="f in FITZPATRICK" :key="f.num" 
                             class="fitz-cell" 
                             :style="{background: f.hex}"
                             @click="pickFitzpatrick(f)">
                          <div class="fitz-num">{{f.num}}</div>
                        </div>
                      </div>
                      <div class="fitz-labels-row">
                        <div v-for="f in FITZPATRICK" :key="'label-'+f.num" class="fitz-label-cell">
                          <div v-for="w in f.name.split(' ')" :key="w">{{w}}</div>
                        </div>
                      </div>
                    </div>
                  </template>

                  <!-- Pilihan undertone (tanpa ilustrasi/teks urat) -->
                  <template v-else-if="block.type === 'interactive_vein_test' || (block.type === 'image' && block.alt === 'Warm vs Cool vs Neutral')">
                    <div class="block">
                      <div class="block-head undertone-block-head">
                        <div>
                          <div class="block-tag">UNDERTONE</div>
                          <div class="block-title">Pilih undertone yang paling sesuai untukmu.</div>
                        </div>
                      </div>
                      <div class="undertone-opts">
                        <div v-for="o in UNDERTONE_OPTS" :key="o.id"
                             class="undertone-opt-card"
                             role="button"
                             tabindex="0"
                             @click="pickUndertone(o)"
                             @keydown.enter.prevent="pickUndertone(o)"
                             @keydown.space.prevent="pickUndertone(o)">
                          <span class="undertone-opt-label">{{ o.label }}</span>
                        </div>
                      </div>
                    </div>
                  </template>

                  <!-- Palet seasonal (swatch/hex) tidak ditampilkan — hanya teks hasil di bubble -->
                  <template v-else-if="block.type === 'season_palette' || block.type === 'palette' || (block.type === 'image' && block.alt && block.alt.startsWith('Palet '))" />

                  <!-- Mascot Seera (buka chat / reset) -->
                  <template v-else-if="block.type === 'mascot_welcome' || (block.type === 'image' && block.alt === 'Maskot Seera')">
                    <div class="block" style="padding: 0; overflow: hidden;">
                      <div class="mascot">
                        <div class="mascot-orb"></div>
                        <div>
                          <div class="mascot-text">Halo, aku <em style="font-style:italic">Seera</em>.</div>
                          <div style="font-size: 13px; color: var(--ink-2); margin-top: 4px;">Asisten warna pribadimu — temukan palette pakaian yang membuatmu bersinar.</div>
                        </div>
                      </div>
                    </div>
                  </template>

                  <template v-else-if="block.type === 'image' || block.type === 'infographic'">
                    <div class="block" style="padding: 10px;">
                      <img :src="block.url" :alt="block.alt" class="multimodal-image" loading="lazy" style="width: 100%; border-radius: 8px;" />
                    </div>
                  </template>
                </div>
              </div>

              <template v-if="msg.text && !msg.blocks">
                <div class="bubble" v-html="formatMessage(msg.text)"></div>
              </template>

              <!-- Products -->
              <div v-if="msg.type === 'products'" class="block" style="margin-top: 8px;">
                <div class="block-head" style="padding: 14px 14px 0;">
                  <div>
                    <div class="block-tag">REKOMENDASI · {{ msg.items.length }} produk</div>
                    <div class="block-title">Untukmu, {{ SEASONS[msg.season?.toLowerCase()]?.name }}</div>
                  </div>
                  <div style="font-size:10px; font-family:var(--font-mono); color:var(--ink-3);">ROC × Y2</div>
                </div>
                <div class="products" style="padding: 0 14px 14px;">
                  <div v-for="(prod, i) in msg.items" :key="i" class="product">
                    <div class="product-thumb">
                       <img v-if="prod.thumbnail_url || prod.image_url" :src="prod.thumbnail_url || prod.image_url" class="product-thumb-bg" style="width: 100%; height: 100%; object-fit: cover;" />
                       <div class="product-score"><em>{{ Math.round((prod.final_score || prod.saw_score) * 100) }}</em>/100</div>
                    </div>
                    <div class="product-info">
                      <div class="product-title">{{ prod.product_name }}</div>
                      <div class="product-price">Rp{{ formatNumber(prod.price) }}</div>
                      <div class="product-swatches">
                        <div v-for="(sw, si) in prod.color_swatches" :key="si" :style="{ backgroundColor: sw.hex_code }"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <button type="button" @click="openFeedbackInline" class="qr primary" v-if="msg.type === 'products' && !msg.feedbackGiven" style="margin-top: 8px; justify-content: center;">
                Beri Rating Sesi Ini
              </button>

              <span class="meta" style="font-size: 10px; color: var(--ink-3); margin-top: 4px; display: block; text-align: right;" v-if="msg.role === 'user'">{{ msg.time }}</span>
              <span class="meta" style="font-size: 10px; color: var(--ink-3); margin-top: 4px; display: block;" v-if="msg.role === 'bot'">{{ msg.time }} <span v-if="msg.latency">· AIML: {{ msg.latency }}</span></span>
            </div>
          </div>

          <!-- Typing -->
          <div v-if="sending" class="msg-row">
            <div class="msg-avatar"></div>
            <div class="msg-stack">
              <div class="typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Replies -->
      <div v-if="currentQuickReplies.length && !showFeedback" class="composer-wrap quick-replies-outer" style="padding-bottom: 8px; padding-top: 8px; position: relative;">
        <div class="quick-replies-row">
          <div class="qr-avatar" aria-hidden="true"></div>
          <div class="quick-replies">
            <button v-for="(qr, i) in currentQuickReplies" :key="i" @click="quickSend(qr.value)" :class="['qr', i === 0 ? 'primary' : '']">
              {{ qr.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="composer-wrap" style="padding-top: 4px;" v-if="!showFeedback">
        <form class="composer" @submit.prevent="handleSend">
          <input
            v-model="inputMessage"
            placeholder="Ketik pesan untuk Seera…"
            style="flex: 1; border: none; outline: none; background: transparent; font-family: var(--font-ui); font-size: 14px; padding: 8px 0; color: var(--ink);"
            :disabled="sending"
          />
          <button type="submit" :disabled="sending || !inputMessage.trim()" class="composer-send" aria-label="Kirim">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </form>
        <div class="composer-foot" style="text-align:center; display:block; margin-top: 6px; font-size:10px; color:var(--ink-3); font-family: var(--font-mono); letter-spacing: 0.02em;">
          <span>AIML 2.0 · FIS Mamdani 2-layer · ROC</span>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="showFeedback" class="feedback-overlay">
        <div class="feedback-panel">
          <h4 style="text-align:center; font-family:var(--font-display); font-size:16px; margin:0 0 12px; color:var(--ink);">Beri rating rekomendasi</h4>
          <div class="star-rating" style="display:flex; justify-content:center; gap:8px; margin-bottom:16px;">
            <button v-for="s in 5" :key="s" @click="feedbackForm.rating = s" :style="{fontSize:'28px', background:'none', border:'none', cursor:'pointer', color: s <= feedbackForm.rating ? '#C97B5C' : '#E8DFD3'}">
              ★
            </button>
          </div>
          <textarea v-model="feedbackForm.comment" placeholder="Komentar tambahan (opsional)..." style="width:100%; border:1px solid var(--line-2); background: #FAFAF7; color: var(--ink); border-radius:8px; padding:10px; font-size:13px; margin-bottom:12px; resize:none; height:60px;"></textarea>
          <div style="display:flex; gap:10px;">
            <button type="button" @click="closeFeedbackPanel" class="qr" style="flex:1; justify-content:center; background:#f0f0f0; border-color:#e0e0e0;">Nanti</button>
            <button @click="submitSessionFeedback" :disabled="!feedbackForm.rating" class="qr primary" style="flex:1; justify-content:center;">Kirim</button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { sendChat, getRecommendations, submitFeedback } from '../services/seeraApi'

const isOpen = ref(false)
const messages = ref([])
const inputMessage = ref('')
const sending = ref(false)
const sessionId = ref('')
const currentQuickReplies = ref([])
const messagesContainer = ref(null)

const showFeedback = ref(false)
const feedbackForm = ref({ rating: 0, comment: '' })

const formatNumber = (v) => new Intl.NumberFormat('id-ID').format(v)
const getTime = () => new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })

const FITZPATRICK = [
  { num: 1, name: "Very Fair", hex: "#F5DBC4", sub: "Fitzpatrick I" },
  { num: 2, name: "Fair", hex: "#EAC2A0", sub: "Fitzpatrick II" },
  { num: 3, name: "Medium Fair", hex: "#D4A382", sub: "Fitzpatrick III" },
  { num: 4, name: "Moderate Brown", hex: "#A87858", sub: "Fitzpatrick IV" },
  { num: 5, name: "Brown", hex: "#7A4F36", sub: "Fitzpatrick V" },
  { num: 6, name: "Dark Brown", hex: "#4A2E20", sub: "Fitzpatrick VI" }
]

const undertoneDisplayKey = (userMsg, apiUndertone) => {
  const m = (userMsg || '').toLowerCase()
  if (m === 'cool' || m === 'warm' || m === 'neutral') return m
  if (m.includes('hijau') || m.includes('hangat')) return 'warm'
  if (m.includes('biru') || m.includes('ungu') || m.includes('dingin')) return 'cool'
  if (m.includes('campuran') || m.includes('netral')) return 'neutral'
  const u = apiUndertone
  const n = typeof u === 'number' ? u : parseFloat(String(u))
  if (!Number.isNaN(n)) {
    if (n <= 0) return 'cool'
    if (n >= 2) return 'warm'
    return 'neutral'
  }
  const s = String(u || '').toLowerCase()
  if (s.includes('warm')) return 'warm'
  if (s.includes('cool')) return 'cool'
  if (s.includes('neutral')) return 'neutral'
  return 'neutral'
}

const UNDERTONE_OPTS = [
  { id: 'cool', label: 'Cool' },
  { id: 'warm', label: 'Warm' },
  { id: 'neutral', label: 'Neutral' }
]

/** True only when the user just submitted undertone (bukan "lihat rekomendasi" dll.). */
const isUndertoneCompletionMessage = (msg) => {
  const raw = (msg || '').trim()
  const m = raw.toLowerCase()
  if (!m) return false
  if (['cool', 'warm', 'neutral'].includes(m)) return true
  if (/^[012]$/.test(m)) return true
  if (UNDERTONE_OPTS.some((o) => o.id === m || o.label.toLowerCase() === m)) return true
  if (m === 'hijau' || m === 'campuran') return true
  if (m.startsWith('biru') || m.includes('ungu')) return true
  return false
}

/** Kembali ke menu awal chat — reset sesi frontend agar permintaan berikutnya pakai session_id baru (hindari error / state kacau). */
const wantsMainMenu = (msg) => {
  const v = (msg || '').trim().toLowerCase().replace(/^🏠\s*/u, '')
  return v === 'menu utama'
}

/** Buka panel rating — jangan kirim ke /chat (backend balas profiling selesai lagi). */
const wantsFeedbackIntent = (msg) => {
  const v = (msg || '').trim().toLowerCase()
  if (!v) return false
  if (v === 'beri feedback' || v.startsWith('beri feedback')) return true
  if (v === 'feedback' || v === 'kirim feedback') return true
  if (v.includes('beri rating') || v.includes('rating sesi')) return true
  return false
}

/** Tombol cepat setelah rekomendasi / selesai rating (rating pakai kartu produk — tanpa duplikat di QR). */
const quickRepliesPostRecommendation = () => [
  { label: 'Rekomendasi lagi', value: 'ulang rekomendasi' },
  { label: 'Ulang Profiling', value: 'Ulang Profiling' },
  { label: 'Menu Utama', value: 'Menu Utama' }
]

const openFeedbackFlow = (userLine) => {
  if (!sessionId.value) {
    pushMsg('bot', 'Selesaikan dan lihat rekomendasi dulu, baru bisa beri rating ya ✨')
    return
  }
  feedbackForm.value = { rating: 0, comment: '' }
  pushMsg('user', userLine)
  currentQuickReplies.value = []
  showFeedback.value = true
}

/** Tombol di dalam chat "Beri Rating Sesi Ini" — tanpa bubble user; QR disembunyikan saat overlay. */
const openFeedbackInline = () => {
  if (!sessionId.value) return
  feedbackForm.value = { rating: 0, comment: '' }
  currentQuickReplies.value = []
  showFeedback.value = true
}

const closeFeedbackPanel = () => {
  showFeedback.value = false
  if (sessionId.value && messages.value.some((m) => m.type === 'products')) {
    currentQuickReplies.value = quickRepliesPostRecommendation()
  }
}

/** Ulang profiling: harus sesi baru — jangan kirim ke API dengan session lama (backend masih punya seasonal). */
const wantsRestartProfiling = (msg) => {
  const v = (msg || '').trim().toLowerCase()
  if (!v) return false
  if (v === 'ulang profiling') return true
  if (v.includes('ulang profiling')) return true
  if (v === 'mulai profiling' && sessionId.value) return true
  return false
}

/** Minta daftar rekomendasi lagi — pakai /recommend saja, jangan /chat (hindari balasan profiling selesai). */
const wantsRefreshRecommendations = (msg) => {
  const v = (msg || '').trim().toLowerCase()
  if (!v) return false
  const hasRekomend = v.includes('rekomend')
  if (!hasRekomend) return false
  if (v.includes('ulang') && hasRekomend) return true
  if (v.includes('refresh') && hasRekomend) return true
  if (v.includes('rekomendasi lagi') || v.includes('rekomend lagi')) return true
  if (v.includes('lihat') && v.includes('rekomend') && (v.includes('lagi') || v.includes('ulang'))) return true
  return false
}

const handleRefreshRecommendations = async (displayText) => {
  pushMsg('user', displayText)
  currentQuickReplies.value = []
  if (!sessionId.value) {
    pushMsg('bot', 'Selesaikan profiling dulu ya, baru bisa minta rekomendasi lagi ✨')
    return
  }
  await generateRecommendation()
}

const wantsCasualThanks = (msg) => {
  const v = (msg || '').trim().toLowerCase()
  if (!v || v.length > 100) return false
  if (/^(terima\s+kasih|terimakasih|makasih|thanks|thank\s*you|tq|thx)\b/.test(v)) return true
  if (/^(sam[ae]\s*sam[ae])\b/.test(v)) return true
  if (v === 'ok' || v === 'oke' || /^okee?\b/.test(v) || v === 'sip' || v === 'siap' || v === 'baik') return true
  return false
}

const wantsGreetingShort = (msg) => {
  const v = (msg || '').trim().toLowerCase()
  return /^(hai|halo|hei|hi|hello)\b/.test(v) && v.length < 48
}

const SEASONS = {
  spring: {
    name: "Spring",
    emoji: "🌸",
    tagline: "Warm · Light · Bright",
    desc: "warm, cerah, dan segar",
    colors: ["#F4A77F", "#F2CB6A", "#A8C77E", "#7BC4C9", "#F4D7C0"]
  },
  summer: {
    name: "Summer",
    emoji: "🌊",
    tagline: "Cool · Light · Soft",
    desc: "lembut, sejuk, dan elegan",
    colors: ["#A8C0D6", "#7FA4C2", "#D5C7E0", "#9CAFB7", "#F2E8E0"]
  },
  autumn: {
    name: "Autumn",
    emoji: "🍂",
    tagline: "Warm · Deep · Earthy",
    desc: "warm, deep, dan earthy",
    colors: ["#A85E40", "#C4863F", "#7B6B47", "#8FA668", "#E8C896"]
  },
  winter: {
    name: "Winter",
    emoji: "❄️",
    tagline: "Cool · Deep · Clear",
    desc: "cool, kontras, dan tegas",
    colors: ["#1B3A6B", "#7A1B3A", "#E8E8E8", "#1F1B16", "#5C2B7A"]
  }
};

const formatMessage = (text) => {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>')
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(messages, scrollToBottom, { deep: true })
watch(currentQuickReplies, scrollToBottom, { deep: true })
watch(sending, scrollToBottom)

const initWelcome = () => {
  if (messages.value.length > 0) return
  
  messages.value = [
    { 
      role: 'bot', 
      blocks: [
        { type: 'mascot_welcome' },
        { type: 'text', content: 'Mau aku bantu cari warna pakaian yang paling cocok untukmu? Kita bisa mulai dengan profiling singkat — tidak perlu foto, hanya 2 pertanyaan. ✨' }
      ],
      time: getTime() 
    }
  ]
  currentQuickReplies.value = [
    { label: 'Mulai Profiling', value: 'Mulai Profiling' },
    { label: 'Belajar Dulu', value: 'Belajar Dulu' },
    { label: 'Apa itu Seera?', value: 'Apa itu Seera?' }
  ]
}

const openChat = () => {
  isOpen.value = true
  initWelcome()
}

const closeChat = () => {
  isOpen.value = false
}

const resetSession = () => {
  sessionId.value = ''
  messages.value = []
  currentQuickReplies.value = []
  showFeedback.value = false
  initWelcome()
}

const pushMsg = (role, blocksOrText, opts = {}) => {
  const msg = { role, time: getTime(), ...opts }
  if (typeof blocksOrText === 'string') {
    msg.text = blocksOrText
  } else {
    msg.blocks = blocksOrText
  }
  messages.value.push(msg)
}

const processResponseAfterChat = async (response, lastUserMsg, startTime) => {
  const latency = `${Date.now() - startTime}ms`
  sessionId.value = response.session_id

  let botText = response.bot_message
  let finalBlocks = response.blocks

  if (botText && botText.includes('Sekarang Pilih undertone:')) {
    botText = 'Bagus. Sekarang pilih undertone yang paling sesuai untukmu.'
    if (!finalBlocks) {
      finalBlocks = [{ type: 'text', content: botText }]
    } else {
      const textBlock = finalBlocks.find((b) => b.type === 'text')
      if (textBlock) textBlock.content = botText
    }
    finalBlocks.push({ type: 'interactive_vein_test' })
  } else if (botText && botText.includes('Profiling selesai. Seasonal type kamu:')) {
    if (wantsRestartProfiling(lastUserMsg)) {
      resetSession()
      return
    }
    if (wantsRefreshRecommendations(lastUserMsg)) {
      currentQuickReplies.value = []
      await generateRecommendation()
      return
    }

    const lowerLast = lastUserMsg.toLowerCase()

    // Backend mengulang teks "Profiling selesai..." untuk setiap chat selama sesi sudah lengkap.
    // Jangan jalankan ulang alur reveal AIML untuk "Lihat Rekomendasi" — langsung ambil produk.
    if (lowerLast.includes('lihat rekomendasi')) {
      currentQuickReplies.value = []
      await generateRecommendation()
      return
    }

    if (wantsFeedbackIntent(lastUserMsg)) {
      feedbackForm.value = { rating: 0, comment: '' }
      showFeedback.value = true
      currentQuickReplies.value = []
      return
    }

    if (!isUndertoneCompletionMessage(lastUserMsg)) {
      pushMsg(
        'bot',
        [
          {
            type: 'text',
            content:
              'Pesanmu sudah kuterima — musim warnamu tetap sama di sesi ini. Lanjut lewat tombol cepat (**Rekomendasi lagi**, **Ulang Profiling**, atau **Menu Utama**) atau ketik pertanyaan soal warna & styling 👇'
          }
        ],
        { latency }
      )
      currentQuickReplies.value = quickRepliesPostRecommendation()
      return
    }

    const seasonKey = (response.seasonal_type || 'summer').toLowerCase()
    const uKey = undertoneDisplayKey(lastUserMsg, response.undertone)

    pushMsg(
      'bot',
      [{ type: 'text', content: `Catat: undertone **${uKey}**. Sebentar, aku hitung musim warnamu… ⏳` }],
      { latency }
    )

    sending.value = true
    await new Promise((r) => setTimeout(r, 1100))
    sending.value = false

    const s = SEASONS[seasonKey] || SEASONS.summer
    const revealBlocks = [
      { type: 'text', content: `Hasilnya: kamu **${s.name}** ${s.emoji} — palette-mu ${s.desc}.` }
    ]
    pushMsg('bot', revealBlocks, { latency: `${Date.now() - startTime}ms` })

    currentQuickReplies.value = [
      { label: 'Lihat Rekomendasi', value: 'lihat rekomendasi' },
      { label: `Pelajari ${s.name}`, value: 'apa itu seasonal color type' },
      { label: 'Reset', value: '__reset_session__' }
    ]
    return
  }

  pushMsg('bot', finalBlocks || [{ type: 'text', content: botText }], { latency })
  currentQuickReplies.value = response.quick_replies || []

  if (
    lastUserMsg.toLowerCase().includes('lihat rekomendasi') ||
    (response.seasonal_type &&
      response.quick_replies?.some((qr) => (qr.value || '').toLowerCase() === 'lihat rekomendasi'))
  ) {
    if (lastUserMsg.toLowerCase().includes('lihat rekomendasi')) {
      await generateRecommendation()
    }
  }
}

const pickFitzpatrick = async (f) => {
  if (sending.value) return
  const text = `${f.name} (${f.sub})`
  pushMsg('user', text)
  sending.value = true
  currentQuickReplies.value = []
  const startTime = Date.now()
  try {
    const response = await sendChat({
      session_id: sessionId.value || null,
      message: text
    })
    await processResponseAfterChat(response, text, startTime)
  } catch (error) {
    pushMsg('bot', `Maaf, terjadi kesalahan: ${error.message}`)
  } finally {
    sending.value = false
  }
}

const pickUndertone = async (o) => {
  if (sending.value) return
  pushMsg('user', o.label)
  sending.value = true
  currentQuickReplies.value = []
  const startTime = Date.now()
  try {
    const response = await sendChat({
      session_id: sessionId.value || null,
      message: o.id
    })
    await processResponseAfterChat(response, o.label, startTime)
  } catch (error) {
    pushMsg('bot', `Maaf, terjadi kesalahan: ${error.message}`)
  } finally {
    sending.value = false
  }
}

const handleSend = async () => {
  const text = inputMessage.value.trim()
  if (!text || sending.value) return

  if (wantsRestartProfiling(text)) {
    inputMessage.value = ''
    resetSession()
    return
  }

  if (wantsMainMenu(text)) {
    inputMessage.value = ''
    resetSession()
    return
  }

  if (wantsFeedbackIntent(text)) {
    inputMessage.value = ''
    openFeedbackFlow(text)
    return
  }

  if (
    sessionId.value &&
    (wantsCasualThanks(text) || wantsGreetingShort(text))
  ) {
    pushMsg('user', text)
    inputMessage.value = ''
    const botLine = wantsCasualThanks(text)
      ? 'Sama-sama ✨ Senang bisa bantu!'
      : 'Hai! Kalau mau lanjut, pilih opsi di bawah atau tanya seputar warna & gaya pakaian.'
    pushMsg('bot', botLine)
    currentQuickReplies.value = quickRepliesPostRecommendation()
    return
  }

  if (wantsRefreshRecommendations(text)) {
    inputMessage.value = ''
    await handleRefreshRecommendations(text)
    return
  }

  pushMsg('user', text)
  inputMessage.value = ''
  sending.value = true
  currentQuickReplies.value = []

  const startTime = Date.now()

  try {
    const response = await sendChat({
      session_id: sessionId.value || null,
      message: text
    })
    await processResponseAfterChat(response, text, startTime)
  } catch (error) {
    pushMsg('bot', `Maaf, terjadi kesalahan: ${error.message}`)
  } finally {
    sending.value = false
  }
}

const quickSend = async (value) => {
  if (value === '__reset_session__') {
    resetSession()
    return
  }
  if (wantsRestartProfiling(value)) {
    resetSession()
    return
  }
  if (wantsMainMenu(value)) {
    resetSession()
    return
  }
  if (wantsFeedbackIntent(value)) {
    openFeedbackFlow(String(value).trim())
    return
  }
  if (wantsRefreshRecommendations(value)) {
    await handleRefreshRecommendations(value)
    return
  }
  inputMessage.value = value
  await handleSend()
}

const generateRecommendation = async () => {
  if (!sessionId.value) return

  sending.value = true
  try {
    const result = await getRecommendations({
      session_id: sessionId.value,
      disable_price: false,
      top_n: 6
    })

    pushMsg('bot', `Ini pilihan terbaikku berdasarkan musimmu, lengkap dengan skor kecocokan ✨`)
    
    messages.value.push({
      role: 'bot',
      type: 'products',
      season: result.seasonal_type,
      items: result.recommendations,
      time: getTime(),
      feedbackGiven: false
    })

    currentQuickReplies.value = quickRepliesPostRecommendation()
  } catch (error) {
    pushMsg('bot', `Gagal memuat rekomendasi: ${error.message}`)
  } finally {
    sending.value = false
  }
}

const submitSessionFeedback = async () => {
  if (!sessionId.value || !feedbackForm.value.rating) return
  
  try {
    await submitFeedback({
      session_id: sessionId.value,
      rating: feedbackForm.value.rating,
      comment: feedbackForm.value.comment
    })
    
    showFeedback.value = false
    pushMsg('bot', "Yay, makasih ya 💖. Mau coba kategori lain atau reset sesi?")
    
    const productMsg = messages.value.slice().reverse().find(m => m.type === 'products')
    if (productMsg) productMsg.feedbackGiven = true

    currentQuickReplies.value = quickRepliesPostRecommendation()
    
  } catch (e) {
    console.error("Gagal kirim feedback", e)
    showFeedback.value = false
    currentQuickReplies.value = quickRepliesPostRecommendation()
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');

.seera-chat-widget {
  /* Ukuran teknis mengikuti lebar panel (AIML + responsif) */
  container-type: inline-size;
  container-name: seera-chat;
  --bg: #F7F2EC;
  --bg-elev: #FBF7F2;
  --bg-card: #FFFFFF;
  --ink: #1F1B16;
  --ink-2: #4A4239;
  --ink-3: #8A7F72;
  --line: #E8DFD3;
  --line-2: #DCD0BF;
  --clay: #C97B5C;
  --clay-deep: #A85E40;
  --sage: #8FA68A;
  --bot-bubble: #FFFFFF;
  --user-bubble: #1F1B16;
  --user-ink: #F7F2EC;
  --shadow-sm: 0 1px 2px rgba(31, 27, 22, 0.04), 0 1px 1px rgba(31, 27, 22, 0.03);
  --shadow-md: 0 4px 16px rgba(31, 27, 22, 0.06), 0 1px 3px rgba(31, 27, 22, 0.04);
  --shadow-lg: 0 24px 48px rgba(31, 27, 22, 0.08), 0 4px 12px rgba(31, 27, 22, 0.04);
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 22px;
  --radius-xl: 28px;
  --font-display: "Cormorant Garamond", Georgia, serif;
  --font-ui: "DM Sans", -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", monospace;
  --fitz-num-size: clamp(14px, 4vw, 18px);
  --fitz-num-box: clamp(19px, 5vw, 24px);
  --fitz-label-size: clamp(7.5px, 2.1vw, 9.5px);
  --fitz-gap: clamp(4px, 1.35vw, 6px);
  --fitz-cell-radius: clamp(8px, 2.1vw, 10px);

  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 10000;
  width: 380px;
  max-width: calc(100vw - 32px);
  height: 600px;
  max-height: calc(100vh - 56px);
  background: var(--bg);
  border-radius: 20px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: var(--font-ui);
  color: var(--ink);
}

@supports (width: 1cqw) {
  .seera-chat-widget {
    --fitz-num-size: clamp(14px, 4.2cqw, 18px);
    --fitz-num-box: clamp(19px, 5.2cqw, 24px);
    --fitz-label-size: clamp(7.5px, 2.15cqw, 9.5px);
    --fitz-gap: clamp(4px, 1.4cqw, 6px);
    --fitz-cell-radius: clamp(8px, 2.2cqw, 10px);
  }
}

.chatbot-bubble-btn {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 9999;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #F2C9B4, #C97B5C 60%, #A85E40);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 24px rgba(201, 123, 92, 0.45), 0 2px 8px rgba(0,0,0,0.15);
  transition: transform 0.3s cubic-bezier(.4,2,.6,1), box-shadow 0.3s;
}
.chatbot-bubble-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 32px rgba(201, 123, 92, 0.6), 0 4px 12px rgba(0,0,0,0.2);
}

.chat-head {
  padding: 16px 24px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg);
  position: relative;
  z-index: 5;
}
.chat-head-left { display: flex; align-items: center; gap: 12px; }
.avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 30% 25%, #FFE4D2, transparent 50%),
    radial-gradient(circle at 70% 70%, #C97B5C, transparent 60%),
    linear-gradient(135deg, #F2C9B4, #A85E40);
  position: relative;
  flex-shrink: 0;
}
.avatar::after {
  content: "";
  position: absolute;
  bottom: -1px; right: -1px;
  width: 10px; height: 10px;
  background: var(--sage);
  border-radius: 50%;
  border: 2px solid var(--bg);
}
.chat-head-name {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
  line-height: 1.1;
}
.chat-head-status {
  font-size: 11px;
  color: var(--ink-3);
}

.chat-head-actions { display: flex; gap: 6px; }
.icon-btn {
  width: 32px; height: 32px;
  border: 1px solid var(--line);
  background: var(--bg-elev);
  border-radius: 10px;
  display: grid; place-items: center;
  cursor: pointer;
  color: var(--ink-2);
  transition: all 0.15s;
}
.icon-btn:hover { background: white; border-color: var(--line-2); }

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px 16px;
  scroll-behavior: smooth;
}
.messages-inner {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.messages::-webkit-scrollbar { width: 6px; }
.messages::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 99px; }

.day-divider {
  text-align: center;
  font-size: 10px;
  color: var(--ink-3);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin: 0 0 8px;
}

.msg-row {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  animation: rise 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}
@keyframes rise {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 26px; height: 26px;
  border-radius: 50%;
  flex-shrink: 0;
  background: linear-gradient(135deg, #F2C9B4, #A85E40);
  margin-bottom: 14px;
}
.msg-row.user .msg-avatar { display: none; }
.msg-stack { display: flex; flex-direction: column; gap: 4px; max-width: 280px; }
.msg-row.user .msg-stack { align-items: flex-end; }

.bubble {
  padding: 10px 14px;
  background: var(--bot-bubble);
  border: 1px solid var(--line);
  border-radius: 16px 16px 16px 4px;
  font-size: 13.5px;
  line-height: 1.5;
  color: var(--ink);
  box-shadow: var(--shadow-sm);
  word-break: break-word;
}
.msg-row.user .bubble {
  background: var(--user-bubble);
  color: var(--user-ink);
  border-color: var(--user-bubble);
  border-radius: 16px 16px 4px 16px;
}
.bubble :deep(em), .bubble :deep(strong) {
  font-style: normal;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 15px;
}

.block {
  background: var(--bot-bubble);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.block-tag {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--ink-3);
  font-family: var(--font-mono);
}
.block-title {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 17px;
  letter-spacing: -0.01em;
}

.quick-replies-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}
.qr-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  flex-shrink: 0;
  background: linear-gradient(135deg, #F2C9B4, #A85E40);
  margin-bottom: 4px;
}
.quick-replies-outer .quick-replies {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
  padding: 0;
}

.mascot {
  background: linear-gradient(135deg, #FBF0E5, #F5DCC9);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  border: 1px solid var(--line);
}
.mascot-orb {
  width: 72px; height: 72px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 30% 30%, #FFE4D2, transparent 60%),
    radial-gradient(circle at 70% 70%, #A85E40, transparent 60%),
    linear-gradient(135deg, #F2C9B4, #C97B5C);
  flex-shrink: 0;
  position: relative;
  animation: float 3s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.mascot-orb::before, .mascot-orb::after {
  content: "";
  position: absolute;
  background: var(--ink);
  width: 5px; height: 5px;
  border-radius: 50%;
  top: 30px;
}
.mascot-orb::before { left: 22px; }
.mascot-orb::after { right: 22px; }

.mascot-text {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 400;
  line-height: 1.35;
  letter-spacing: -0.01em;
}

.fitz {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--fitz-gap);
}
.fitz-grid-wrap {
  padding: clamp(10px, 2.85vw, 14px);
}
.fitz-labels-row {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--fitz-gap);
  padding: 0 clamp(10px, 2.85vw, 14px) clamp(10px, 2.85vw, 14px);
}
@supports (width: 1cqw) {
  .seera-chat-widget .fitz-grid-wrap {
    padding: clamp(10px, 3cqw, 14px);
  }
  .seera-chat-widget .fitz-labels-row {
    padding: 0 clamp(10px, 3cqw, 14px) clamp(10px, 3cqw, 14px);
  }
}
.fitz-label-cell {
  font-size: var(--fitz-label-size);
  color: var(--ink-3);
  text-align: center;
  line-height: 1.2;
  font-family: var(--font-mono);
}
.fitz-cell {
  aspect-ratio: 1 / 1.3;
  border-radius: var(--fitz-cell-radius);
  position: relative;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: clamp(4px, 1.35vw, 6px);
  border: 2px solid transparent;
  transition: all 0.2s;
}
@supports (width: 1cqw) {
  .seera-chat-widget .fitz-cell {
    padding: clamp(4px, 1.4cqw, 6px);
  }
}
.fitz-cell:hover { transform: translateY(-2px); }
.fitz-cell.selected {
  border-color: var(--ink);
  box-shadow: 0 0 0 3px rgba(31,27,22,0.08);
}
.fitz-num {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: var(--fitz-num-size);
  line-height: 1;
  background: rgba(255,255,255,0.9);
  width: var(--fitz-num-box);
  height: var(--fitz-num-box);
  min-width: var(--fitz-num-box);
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: var(--ink);
}

.undertone-block-head {
  padding: 14px 14px 0;
}

.undertone-opts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(8px, 2.2vw, 10px);
  padding: 14px;
}

.undertone-opt-card {
  background: var(--bg-elev);
  border-radius: 14px;
  padding: 14px 10px;
  cursor: pointer;
  text-align: center;
  border: 1px solid var(--line);
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.undertone-opt-card:hover {
  transform: translateY(-2px);
  border-color: var(--line-2);
}

.undertone-opt-card:focus-visible {
  outline: 2px solid var(--ink-3);
  outline-offset: 2px;
}

.undertone-opt-label {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0.02em;
}

.typing {
  display: inline-flex;
  gap: 4px;
  padding: 12px 14px;
  background: var(--bot-bubble);
  border: 1px solid var(--line);
  border-radius: 16px 16px 16px 4px;
  width: fit-content;
}
.typing span {
  width: 6px; height: 6px;
  background: var(--ink-3);
  border-radius: 50%;
  animation: typing 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.15s; }
.typing span:nth-child(3) { animation-delay: 0.3s; }
@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-3px); }
}

.composer-wrap {
  padding: 0 20px 16px;
  background: linear-gradient(180deg, transparent, var(--bg) 20%);
}
.composer {
  background: var(--bg-card);
  border: 1px solid var(--line-2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  padding: 4px 6px 4px 14px;
  gap: 8px;
  box-shadow: var(--shadow-md);
  transition: border-color 0.15s;
}
.composer:focus-within { border-color: var(--ink-3); }

.composer-send {
  width: 32px; height: 32px;
  background: var(--ink);
  color: var(--bg);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: grid; place-items: center;
  flex-shrink: 0;
  transition: all 0.15s;
}
.composer-send:hover { background: var(--clay); }
.composer-send:disabled { opacity: 0.4; cursor: not-allowed; }

.qr {
  background: var(--bg-elev);
  border: 1px solid var(--line-2);
  color: var(--ink);
  padding: 6px 12px;
  border-radius: 99px;
  font-size: 12px;
  font-family: var(--font-ui);
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}
.qr:hover {
  background: var(--ink);
  color: var(--bg);
  border-color: var(--ink);
}
.qr.primary {
  background: var(--clay);
  color: white;
  border-color: var(--clay);
}
.qr.primary:hover { background: var(--clay-deep); border-color: var(--clay-deep); }

.products {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.product {
  background: var(--bg-elev);
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
}
.product:hover {
  border-color: var(--ink-3);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.product-thumb {
  aspect-ratio: 4 / 5;
  position: relative;
  overflow: hidden;
  background: var(--line);
}
.product-score {
  position: absolute;
  top: 8px; right: 8px;
  background: rgba(31,27,22,0.92);
  color: var(--bg);
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 8px;
  font-weight: 500;
  letter-spacing: 0.02em;
}
.product-score em {
  font-family: var(--font-display);
  font-style: normal;
  font-size: 13px;
  margin-right: 2px;
}
.product-info {
  padding: 10px 12px 12px;
}
.product-title {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.3;
  margin-bottom: 4px;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.product-price {
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--ink-2);
}
.product-swatches {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}
.product-swatches > div {
  width: 14px; height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.08);
}

.feedback-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  background: rgba(247,242,236,0.95);
  backdrop-filter: blur(4px);
  padding: 20px;
  border-top: 1px solid var(--line);
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  z-index: 100;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
}

.chat-panel-enter-active { animation: panelIn 0.35s cubic-bezier(0.2, 0.8, 0.2, 1); }
.chat-panel-leave-active { animation: panelOut 0.25s ease-in; }

@keyframes panelIn {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes panelOut {
  from { opacity: 1; transform: translateY(0) scale(1); }
  to { opacity: 0; transform: translateY(20px) scale(0.95); }
}

@media (max-width: 480px) {
  .seera-chat-widget {
    bottom: 0; right: 0;
    width: 100vw; height: 100vh;
    max-height: 100vh; border-radius: 0;
  }
  .chatbot-bubble-btn {
    bottom: 20px; right: 20px;
    width: 54px; height: 54px;
  }
}
</style>
