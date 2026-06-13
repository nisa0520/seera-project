<template>
  <div class="seera-chatbot">
    <button
      class="seera-chatbot__launcher"
      :class="{ 'is-open': isOpen }"
      :aria-label="isOpen ? 'Tutup chatbot Seera' : 'Buka chatbot Seera'"
      @click="toggleOpen"
    >
      <span v-if="!isOpen" class="seera-chatbot__launcher-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path
            d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5z"
            stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"
          />
        </svg>
      </span>
      <span v-else class="seera-chatbot__launcher-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
        </svg>
      </span>
      <span v-if="!isOpen" class="seera-chatbot__launcher-label">Seera</span>
    </button>

    <transition name="seera-fade">
      <section v-if="isOpen" class="seera-chatbot__window" role="dialog" aria-label="Seera Chatbot">
        <header class="seera-chatbot__header">
          <div class="seera-chatbot__head-left">
            <div class="seera-chatbot__avatar" />
            <div>
              <div class="seera-chatbot__title">Seera</div>
              <div class="seera-chatbot__subtitle">● Online</div>
            </div>
          </div>
          <div class="seera-chatbot__head-actions">
            <button class="seera-chatbot__icon-btn" title="Reset sesi" @click="resetSession">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path d="M3 12a9 9 0 0 1 15.5-6.3M21 4v5h-5M21 12a9 9 0 0 1-15.5 6.3M3 20v-5h5"
                  stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
            <button class="seera-chatbot__icon-btn" title="Tutup" @click="close">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>
        </header>

        <div ref="messagesEl" class="seera-chatbot__messages">
          <div class="seera-chatbot__day">Hari ini · {{ todayLabel }}</div>

          <div
            v-for="(item, idx) in messages"
            :key="idx"
            class="seera-chatbot__row"
            :class="{ 'is-user': item.role === 'user' }"
            :data-message-index="idx"
          >
            <div v-if="item.role !== 'user'" class="seera-chatbot__row-avatar" />
            <div
              class="seera-chatbot__row-stack"
              :class="{ 'seera-chatbot__row-stack--wide': item.kind === 'gender' || item.kind === 'fitz' || item.kind === 'undertone' || item.kind === 'education' }"
            >
              <!-- User bubble -->
              <div v-if="item.role === 'user'" class="seera-chatbot__bubble seera-chatbot__bubble--user">
                {{ item.text }}
              </div>

              <template v-else>
                <!-- Text bubble -->
                <div v-if="item.text && item.kind !== 'education'" class="seera-chatbot__bubble" v-html="formatBubble(item.text)" />

                <!-- ═══ Education content ═══ -->
                <div v-if="item.kind === 'education' && item.education" class="seera-chatbot__bubble seera-chatbot__bubble--education">
                  <div class="seera-education__eyebrow">EDUKASI PERSONAL COLOR</div>
                  <div class="seera-education__title">{{ item.education.title }}</div>
                  <div
                    v-if="item.education.intro"
                    class="seera-education__text"
                    v-html="formatBubble(item.education.intro)"
                  />
                  <div v-if="item.education.cards.length" class="seera-education__cards">
                    <div
                      v-for="card in item.education.cards"
                      :key="card.title"
                      class="seera-education__card"
                      :style="{
                        '--education-card-accent': card.accent,
                        '--education-card-bg': card.bg
                      }"
                    >
                      <div class="seera-education__card-head">
                        <span v-if="card.showSwatch" class="seera-education__card-swatch" aria-hidden="true" />
                        <div class="seera-education__card-title">{{ card.title }}</div>
                      </div>
                      <div class="seera-education__card-body" v-html="formatBubble(card.body)" />
                    </div>
                  </div>
                  <div v-if="item.education.steps.length" class="seera-education__steps">
                    <div
                      v-for="step in item.education.steps"
                      :key="step.number"
                      class="seera-education__step"
                    >
                      <div class="seera-education__step-num">{{ step.number }}</div>
                      <div class="seera-education__step-copy">
                        <div class="seera-education__step-title">{{ step.title }}</div>
                        <div class="seera-education__step-body" v-html="formatBubble(step.body)" />
                      </div>
                    </div>
                  </div>
                  <div
                    v-if="!item.education.steps.length && !item.education.cards.length"
                    class="seera-education__text"
                    v-html="formatBubble(item.education.content)"
                  />
                  <div
                    v-if="item.education.outro"
                    class="seera-education__note"
                    v-html="formatBubble(item.education.outro)"
                  />
                </div>

                <!-- ═══ Gender / collection preference selector ═══ -->
                <div v-if="item.kind === 'gender'" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-tag">PREFERENSI KOLEKSI</div>
                  <div class="seera-chatbot__block-title">Koleksi apa yang paling nyaman untukmu?</div>
                  <div class="seera-gender">
                    <div
                      v-for="g in GENDER_DATA"
                      :key="g.id"
                      class="seera-gender__card"
                      :class="{
                        'seera-gender__card--selected': selectedGender === g.id,
                        'seera-gender__card--disabled': loading || idx !== lastBotIndex
                      }"
                      @click="!loading && idx === lastBotIndex && pickGender(g)"
                      role="button"
                      :tabindex="idx === lastBotIndex && !loading ? 0 : -1"
                      :aria-label="g.aria"
                      @keydown.enter="!loading && idx === lastBotIndex && pickGender(g)"
                    >
                      <div class="seera-gender__cap">{{ g.label }}</div>
                      <div class="seera-gender__hint">{{ g.hint }}</div>
                    </div>
                  </div>
                </div>

                <!-- ═══ Fitzpatrick skin tone selector ═══ -->
                <div v-if="item.kind === 'fitz'" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-tag">FITZPATRICK SCALE · I–VI</div>
                  <div class="seera-chatbot__block-title">Mana yang paling mirip kulitmu?</div>
                  <div class="seera-fitz">
                    <div
                      v-for="f in FITZPATRICK_DATA"
                      :key="f.code"
                      class="seera-fitz__cell"
                      :class="{
                        'seera-fitz__cell--selected': selectedSkinTone === f.code,
                        'seera-fitz__cell--disabled': loading || idx !== lastBotIndex
                      }"
                      :style="{ background: f.hex }"
                      @click="!loading && idx === lastBotIndex && pickSkinTone(f)"
                      role="button"
                      :tabindex="idx === lastBotIndex && !loading ? 0 : -1"
                      :aria-label="`${f.name} — Fitzpatrick ${f.code}`"
                      @keydown.enter="!loading && idx === lastBotIndex && pickSkinTone(f)"
                    >
                      <div class="seera-fitz__num">{{ f.num }}</div>
                    </div>
                  </div>
                  <div class="seera-fitz__labels">
                    <div v-for="f in FITZPATRICK_DATA" :key="f.code" class="seera-fitz__label">
                      <span v-for="(word, wi) in f.name.split(' ')" :key="wi">{{ word }}</span>
                    </div>
                  </div>
                  <div class="seera-chatbot__block-actions">
                    <button
                      class="seera-chatbot__qr"
                      :disabled="loading || idx !== lastBotIndex"
                      @click="idx === lastBotIndex && !loading && handleQuickReply({ label: 'Edukasi personal color', value: 'EDUCATION' })"
                    >
                      Edukasi personal color
                    </button>
                  </div>
                </div>

                <!-- ═══ Undertone selector (tanpa urat nadi) ═══ -->
                <div v-if="item.kind === 'undertone'" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-tag">UNDERTONE</div>
                  <div class="seera-chatbot__block-title">Undertone kulitmu cenderung apa?</div>
                  <div class="seera-undertone">
                    <div
                      v-for="u in UNDERTONE_DATA"
                      :key="u.id"
                      class="seera-undertone__card"
                      :class="{
                        'seera-undertone__card--selected': selectedUndertone === u.id,
                        'seera-undertone__card--disabled': loading || idx !== lastBotIndex
                      }"
                      @click="!loading && idx === lastBotIndex && pickUndertone(u)"
                      role="button"
                      :tabindex="idx === lastBotIndex && !loading ? 0 : -1"
                      @keydown.enter="!loading && idx === lastBotIndex && pickUndertone(u)"
                    >
                      <div class="seera-undertone__cap">{{ u.cap }}</div>
                    </div>
                  </div>
                  <div class="seera-undertone__hint">Lihat di bawah cahaya alami untuk hasil terbaik.</div>
                </div>

                <!-- ═══ Summary ═══ -->
                <div v-if="item.kind === 'summary' && item.summary" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-tag">RINGKASAN</div>
                  <div class="seera-chatbot__summary">
                    <div><strong>Koleksi:</strong> {{ item.summary.gender_name }}</div>
                    <div><strong>Skin tone:</strong> {{ item.summary.skin_tone_name }} ({{ item.summary.skin_tone }})</div>
                    <div><strong>Undertone:</strong> {{ item.summary.undertone_name }}</div>
                  </div>
                </div>

                <!-- ═══ Seasonal result — gaya AIML PaletteBlock, tanpa swatch ═══ -->
                <div v-if="item.kind === 'seasonal' && item.seasonal" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-head">
                    <div>
                      <div class="seera-chatbot__block-tag">
                        PALETTE · {{ seasonalTagline(item.seasonal.seasonal_type) }}
                      </div>
                      <div class="seera-chatbot__block-title">
                        {{ item.seasonal.seasonal_name }} {{ seasonalEmoji(item.seasonal.seasonal_type) }}
                      </div>
                    </div>
                  </div>
                  <div class="seera-chatbot__seasonal-membership">
                    <div
                      v-for="(value, label) in item.seasonal.membership"
                      :key="label"
                      class="seera-chatbot__seasonal-row"
                    >
                      <span>{{ label }}</span>
                      <span class="seera-chatbot__bar">
                        <span class="seera-chatbot__bar-fill" :style="{ width: percent(value) + '%' }" />
                      </span>
                      <span class="seera-chatbot__bar-value">{{ percent(value) }}%</span>
                    </div>
                  </div>
                  <div class="seera-chatbot__palette-foot">
                    <span
                      class="seera-chatbot__palette-dot"
                      :style="{ background: seasonalAccent(item.seasonal.seasonal_type) }"
                    />
                    Palette {{ item.seasonal.seasonal_name.toLowerCase() }} cocok untuk karakter
                    {{ seasonalDesc(item.seasonal.seasonal_type) }}.
                  </div>
                </div>

                <!-- ═══ Products ═══ -->
                <div v-if="item.kind === 'products' && item.items" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-head">
                    <div>
                      <div class="seera-chatbot__block-tag">REKOMENDASI · {{ item.items.length }} PRODUK</div>
                      <div class="seera-chatbot__block-title">Pilihan terbaik untukmu</div>
                    </div>
                    <div class="seera-chatbot__chip">FIS × ROC</div>
                  </div>
                  <div class="seera-chatbot__products">
                    <div v-for="p in item.items" :key="p.product_id" class="seera-chatbot__product">
                      <div class="seera-chatbot__product-thumb" :style="{ background: thumbBg(p) }">
                        <span class="seera-chatbot__product-score">
                          <em>{{ Math.round(p.product_score * 100) }}</em>/100
                        </span>
                        <span class="seera-chatbot__product-rank">#{{ p.rank }}</span>
                        <button
                          type="button"
                          class="seera-chatbot__product-action"
                          :aria-label="`Lihat detail produk ${p.product_name}`"
                          @click.stop="goToProductDetail(p)"
                        >
                          Lihat detail produk
                        </button>
                      </div>
                      <div class="seera-chatbot__product-info">
                        <div class="seera-chatbot__product-title">{{ p.product_name }}</div>
                        <div class="seera-chatbot__product-meta">
                          <span class="seera-chatbot__product-price">{{ formatCurrency(p.price) }}</span>
                          <span v-if="p.rating !== null" class="seera-chatbot__product-rating">★ {{ p.rating.toFixed(1) }}</span>
                        </div>
                        <div class="seera-chatbot__product-label">{{ p.label_indonesian }}</div>
                        <div class="seera-chatbot__product-swatches">
                          <span
                            v-for="c in p.colors"
                            :key="c.hex_code"
                            class="seera-chatbot__swatch-dot"
                            :style="{ background: c.hex_code }"
                            :title="`${c.color_name} (${c.label_indonesian})`"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ═══ Colors to avoid ═══ -->
                <div v-if="item.kind === 'avoid' && item.colors" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-tag">WARNA YANG SEBAIKNYA DIHINDARI</div>
                  <div class="seera-chatbot__avoid-list">
                    <div v-for="c in item.colors" :key="c.hex_code" class="seera-chatbot__avoid-item">
                      <span class="seera-chatbot__avoid-swatch" :style="{ background: c.hex_code }" />
                      <div>
                        <div class="seera-chatbot__avoid-name">{{ c.color_name }} <span class="seera-chatbot__mono">{{ c.hex_code }}</span></div>
                        <div class="seera-chatbot__avoid-reason">{{ c.reason }}</div>
                      </div>
                    </div>
                    <div v-if="!item.colors.length" class="seera-chatbot__empty">Tidak ada warna yang perlu dihindari secara khusus.</div>
                  </div>
                </div>

                <!-- ═══ Feedback ═══ -->
                <div v-if="item.kind === 'feedback'" class="seera-chatbot__block">
                  <div class="seera-chatbot__block-tag">FEEDBACK</div>
                  <div class="seera-chatbot__block-title">Bagaimana rekomendasinya?</div>
                  <div class="seera-chatbot__feedback">
                    <button
                      v-for="n in 5"
                      :key="n"
                      class="seera-chatbot__star"
                      :class="{ active: feedbackRating >= n }"
                      @click="feedbackRating = n"
                      :aria-label="`Beri rating ${n}`"
                    >★</button>
                  </div>
                  <textarea
                    v-model="feedbackComment"
                    rows="2"
                    placeholder="Komentar (opsional)"
                    class="seera-chatbot__feedback-text"
                  />
                  <div class="seera-chatbot__feedback-actions">
                    <button class="seera-chatbot__qr seera-chatbot__qr--primary" @click="submitFeedback(false)">Kirim</button>
                    <button class="seera-chatbot__qr" @click="submitFeedback(true)">Lewati</button>
                  </div>
                </div>

                <!-- Quick replies — tidak tampil untuk selector khusus -->
                <div
                  v-if="item.quick_replies && idx === lastBotIndex && !loading && item.kind !== 'gender' && item.kind !== 'fitz' && item.kind !== 'undertone'"
                  class="seera-chatbot__quick-replies"
                >
                  <button
                    v-for="qr in item.quick_replies"
                    :key="qr.value || qr.label"
                    class="seera-chatbot__qr"
                    :class="{ 'seera-chatbot__qr--primary': qr.primary }"
                    @click="handleQuickReply(qr)"
                  >
                    {{ qr.label }}
                  </button>
                </div>
              </template>
            </div>
          </div>

          <div v-if="loading" class="seera-chatbot__row">
            <div class="seera-chatbot__row-avatar" />
            <div class="seera-chatbot__row-stack">
              <div class="seera-chatbot__typing"><span /><span /><span /></div>
            </div>
          </div>
        </div>

        <form class="seera-chatbot__composer" @submit.prevent="sendFreeText">
          <textarea
            v-model="composer"
            rows="1"
            placeholder="Ketik pesan untuk Seera…"
            @keydown.enter.exact.prevent="sendFreeText"
            :disabled="loading"
          />
          <button
            type="submit"
            class="seera-chatbot__send"
            :disabled="!composer.trim() || loading"
            aria-label="Kirim"
          >
            <svg viewBox="0 0 24 24" width="18" height="18">
              <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
        </form>
      </section>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { chatbotApi } from '../../api/chatbot'

// ── Static data ──────────────────────────────────────────────────────────────

const GENDER_DATA = [
  {
    id: 'male',
    code: 'MALE',
    label: 'Pria',
    hint: 'Koko dan atasan pria',
    aria: 'Pilih koleksi pria',
  },
  {
    id: 'female',
    code: 'FEMALE',
    label: 'Wanita',
    hint: 'Gamis, abaya, hijab',
    aria: 'Pilih koleksi wanita',
  },
  {
    id: 'all',
    code: 'PREFER_NOT_TO_SAY',
    label: 'Semua',
    hint: 'Lihat semua koleksi',
    aria: 'Pilih semua koleksi',
  },
]

const FITZPATRICK_DATA = [
  { num: 1, code: 'I',   name: 'Very Fair',      hex: '#F5DBC4' },
  { num: 2, code: 'II',  name: 'Fair',            hex: '#EAC2A0' },
  { num: 3, code: 'III', name: 'Medium Fair',     hex: '#D4A382' },
  { num: 4, code: 'IV',  name: 'Moderate Brown',  hex: '#A87858' },
  { num: 5, code: 'V',   name: 'Brown',           hex: '#7A4F36' },
  { num: 6, code: 'VI',  name: 'Dark Brown',      hex: '#4A2E20' },
]

const UNDERTONE_DATA = [
  { id: 'cool',    code: 'COOL',    label: 'Biru / Ungu',      cap: 'Cool' },
  { id: 'neutral', code: 'NEUTRAL', label: 'Campuran',         cap: 'Neutral' },
  { id: 'warm',    code: 'WARM',    label: 'Hijau / Kuning',   cap: 'Warm' },
]

const SEASONAL_EDUCATION_CARD_STYLE = { accent: '#b88f6b', bg: '#fffaf5' }

const EDUCATION_CARD_TOPICS = new Set(['SKIN_TONE', 'UNDERTONE', 'SEASONAL_COLOR_TYPE'])

const EDUCATION_CARD_STYLE = {
  SKIN_TONE: {
    Putih: { accent: '#f2c4b6', bg: '#fff8f4' },
    'Kuning langsat': { accent: '#e1b95f', bg: '#fff9e8' },
    'Sawo matang': { accent: '#9f6748', bg: '#fff5ed' },
  },
  UNDERTONE: {
    Warm: { accent: '#d88a47', bg: '#fff7ef' },
    Cool: { accent: '#7f93c8', bg: '#f7f9ff' },
    Neutral: { accent: '#8c8178', bg: '#faf8f4' },
  },
  SEASONAL_COLOR_TYPE: {
    Spring: SEASONAL_EDUCATION_CARD_STYLE,
    Summer: SEASONAL_EDUCATION_CARD_STYLE,
    Autumn: SEASONAL_EDUCATION_CARD_STYLE,
    Winter: SEASONAL_EDUCATION_CARD_STYLE,
  },
}

const EDUCATION_TOPIC_CODES = new Set([
  'SKIN_TONE',
  'UNDERTONE',
  'SEASONAL_COLOR_TYPE',
  'DETERMINE_SKIN_TONE',
  'DETERMINE_UNDERTONE',
])

const RESERVED_QUICK_REPLY_VALUES = new Set([
  'START_PROFILING',
  'EDUCATION',
  'START_RECOMMENDATION',
  'COLORS_TO_AVOID',
  'FEEDBACK',
  'FILTER_PRICE_ASC',
  'FILTER_RATING_DESC',
  'FILTER_POPULARITY_DESC',
  'CONFIRM',
  'CHANGE_GENDER',
  'CHANGE_SKIN_TONE',
  'CHANGE_UNDERTONE',
])

const SEASONS_INFO = {
  SPRING: { tagline: 'Warm · Light · Bright', desc: 'warm, cerah, dan segar',       accent: '#F4A77F' },
  SUMMER: { tagline: 'Cool · Light · Soft',   desc: 'lembut, sejuk, dan elegan',    accent: '#A8C0D6' },
  AUTUMN: { tagline: 'Warm · Deep · Earthy',  desc: 'warm, deep, dan earthy',       accent: '#A85E40' },
  WINTER: { tagline: 'Cool · Deep · Clear',   desc: 'cool, kontras, dan tegas',     accent: '#1B3A6B' },
}

const SEASON_EMOJI = { SPRING: '🌸', SUMMER: '🌊', AUTUMN: '🍂', WINTER: '❄️' }

// ── Reactive state ────────────────────────────────────────────────────────────

const isOpen = ref(false)
const messages = ref([])
const loading = ref(false)
const sessionId = ref(null)
const conversationState = ref(null)
const composer = ref('')
const feedbackRating = ref(0)
const feedbackComment = ref('')
const selectedGender = ref(null)
const selectedSkinTone = ref(null)
const selectedUndertone = ref(null)
const changingTarget = ref(null)
const messagesEl = ref(null)
const savedMessagesScrollTop = ref(0)
const restoreMessagesToBottom = ref(false)
const router = useRouter()

// ── Computed ──────────────────────────────────────────────────────────────────

const todayLabel = computed(() =>
  new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long' })
)

const lastBotIndex = computed(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].role === 'bot') return i
  }
  return -1
})

// ── Helpers ───────────────────────────────────────────────────────────────────

function seasonalEmoji(code) { return SEASON_EMOJI[code] || '' }
function seasonalTagline(code) { return SEASONS_INFO[code]?.tagline || '' }
function seasonalDesc(code) { return SEASONS_INFO[code]?.desc || '' }
function seasonalAccent(code) { return SEASONS_INFO[code]?.accent || '#C97B5C' }

function percent(value) {
  if (typeof value !== 'number') return 0
  return Math.round(value * 100)
}

function formatCurrency(num) {
  if (num == null) return '-'
  return 'Rp ' + Number(num).toLocaleString('id-ID')
}

function formatBubble(text) {
  if (!text) return ''
  return String(text).replace(/\n/g, '<br/>')
}

function trimLines(lines) {
  const out = [...lines]
  while (out.length && !out[0].trim()) out.shift()
  while (out.length && !out[out.length - 1].trim()) out.pop()
  return out
}

function linesToText(lines) {
  return trimLines(lines).join('\n')
}

function splitStepOutro(step) {
  const parts = step.body.split(/\n\s*\n(?=Setelah tahu )/)
  if (parts.length < 2) return { step, outro: '' }
  return {
    step: { ...step, body: parts[0].trim() },
    outro: parts.slice(1).join('\n\n').trim(),
  }
}

function finalizeEducationStep(step) {
  return {
    number: step.number,
    title: step.title,
    body: linesToText(step.bodyLines),
  }
}

function finalizeEducationCard(card, topicCode) {
  const style = EDUCATION_CARD_STYLE[topicCode]?.[card.title] || {}
  return {
    title: card.title,
    body: linesToText(card.bodyLines),
    accent: style.accent || '#c97b5c',
    bg: style.bg || '#fffaf5',
    showSwatch: topicCode !== 'SEASONAL_COLOR_TYPE',
  }
}

function parseEducationCards(lines, topicCode) {
  if (!EDUCATION_CARD_TOPICS.has(topicCode)) {
    return { intro: '', cards: [] }
  }

  const introLines = []
  const cards = []
  let current = null

  for (const rawLine of lines) {
    const line = rawLine.trim()
    const match = line.match(/^(?:[-*]|\u2022|\u00e2\u20ac\u00a2)\s*(.+?):\s*(.*)$/)

    if (match) {
      if (current) cards.push(finalizeEducationCard(current, topicCode))
      current = {
        title: match[1].trim(),
        bodyLines: match[2] ? [match[2].trim()] : [],
      }
    } else if (current) {
      current.bodyLines.push(rawLine)
    } else {
      introLines.push(rawLine)
    }
  }

  if (current) cards.push(finalizeEducationCard(current, topicCode))

  return {
    intro: cards.length ? linesToText(introLines) : '',
    cards,
  }
}

function buildEducationContent(data) {
  const content = data.content || ''
  const lines = String(content).split(/\r?\n/)
  const topicCode = data.topic_code || ''
  const introLines = []
  const steps = []
  let current = null

  for (const rawLine of lines) {
    const line = rawLine.trim()
    const match = line.match(/^(\d+)\.\s+(.+?)\.?$/)
    if (match) {
      if (current) steps.push(finalizeEducationStep(current))
      current = {
        number: match[1],
        title: match[2].replace(/\.$/, ''),
        bodyLines: [],
      }
    } else if (current) {
      current.bodyLines.push(rawLine)
    } else {
      introLines.push(rawLine)
    }
  }

  if (current) steps.push(finalizeEducationStep(current))

  let outro = ''
  if (steps.length) {
    const last = splitStepOutro(steps[steps.length - 1])
    steps[steps.length - 1] = last.step
    outro = last.outro
  }

  const cardContent = steps.length
    ? { intro: '', cards: [] }
    : parseEducationCards(lines, topicCode)

  return {
    title: data.title,
    topicCode,
    content,
    intro: steps.length ? linesToText(introLines) : cardContent.intro,
    steps,
    cards: cardContent.cards,
    outro,
  }
}

function thumbBg(product) {
  if (product.image_url) {
    const imageUrl = String(product.image_url)
    if (/^(linear-gradient|radial-gradient|url\()/i.test(imageUrl)) return imageUrl
    return `url("${imageUrl.replace(/"/g, '\\"')}") center / cover no-repeat`
  }
  if (product.colors && product.colors.length) {
    const stops = product.colors.map((c) => c.hex_code).slice(0, 3).join(',')
    return `linear-gradient(160deg, ${stops})`
  }
  return 'linear-gradient(160deg, #F2C9B4, #C97B5C)'
}

function goToProductDetail(product) {
  const id = product?.product_id
  if (!id) return
  rememberMessagesScroll()
  restoreMessagesToBottom.value = true
  router.push({ name: 'ProductDetail', params: { id } }).finally(() => close())
}

function rememberMessagesScroll() {
  if (messagesEl.value) savedMessagesScrollTop.value = messagesEl.value.scrollTop
}

function setMessagesScrollTop(scrollTop, behavior = 'auto') {
  const container = messagesEl.value
  if (!container) return

  const maxScrollTop = Math.max(container.scrollHeight - container.clientHeight, 0)
  const nextScrollTop = Math.max(0, Math.min(scrollTop, maxScrollTop))

  if (typeof container.scrollTo === 'function') {
    container.scrollTo({ top: nextScrollTop, behavior })
  } else {
    container.scrollTop = nextScrollTop
  }

  savedMessagesScrollTop.value = nextScrollTop
}

function restoreMessagesScroll() {
  nextTick(() => {
    if (!messagesEl.value) return
    const maxScrollTop = Math.max(messagesEl.value.scrollHeight - messagesEl.value.clientHeight, 0)
    const nextScrollTop = restoreMessagesToBottom.value
      ? maxScrollTop
      : savedMessagesScrollTop.value

    setMessagesScrollTop(nextScrollTop)
    restoreMessagesToBottom.value = false
  })
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) setMessagesScrollTop(messagesEl.value.scrollHeight)
  })
}

function scrollToMessage(index) {
  nextTick(() => {
    const container = messagesEl.value
    if (!container || !Number.isInteger(index)) return

    const row = container.querySelector(`[data-message-index="${index}"]`)
    if (!row) return

    const containerRect = container.getBoundingClientRect()
    const rowRect = row.getBoundingClientRect()
    const targetTop = container.scrollTop + rowRect.top - containerRect.top - 10
    setMessagesScrollTop(targetTop, 'smooth')
  })
}

function pushUser(text, options = {}) {
  const index = messages.value.length
  messages.value.push({ role: 'user', text })
  if (options.scroll !== false) scrollToBottom()
  return index
}

function pushBot(payload, options = {}) {
  const index = messages.value.length
  messages.value.push({ role: 'bot', ...payload })
  if (options.scroll !== false) scrollToBottom()
  return index
}

function botKindForState(data) {
  if (data.summary) return 'summary'
  if (data.conversation_state === 'WAITING_GENDER') return 'gender'
  if (data.conversation_state === 'WAITING_SKIN_TONE') return 'fitz'
  if (data.conversation_state === 'WAITING_UNDERTONE') return 'undertone'
  return null
}

// ── Session control ───────────────────────────────────────────────────────────

function toggleOpen() {
  if (isOpen.value) {
    close()
    return
  }

  isOpen.value = true
  if (!sessionId.value) {
    startConversation()
  } else {
    restoreMessagesScroll()
  }
}

function close() {
  rememberMessagesScroll()
  isOpen.value = false
}

async function resetSession() {
  messages.value = []
  sessionId.value = null
  conversationState.value = null
  selectedGender.value = null
  selectedSkinTone.value = null
  selectedUndertone.value = null
  changingTarget.value = null
  feedbackRating.value = 0
  feedbackComment.value = ''
  await startConversation()
}

async function startConversation() {
  loading.value = true
  try {
    selectedGender.value = null
    selectedSkinTone.value = null
    selectedUndertone.value = null
    const data = await chatbotApi.start()
    sessionId.value = data.session_id
    conversationState.value = data.conversation_state
    pushBot({ text: data.message, kind: 'gender' })
  } catch {
    pushBot({ text: 'Tidak bisa terhubung ke server Seera. Pastikan backend berjalan di http://localhost:8000.' })
  } finally {
    loading.value = false
  }
}

async function restartProfiling() {
  loading.value = true
  try {
    const data = await chatbotApi.start()
    sessionId.value = data.session_id
    conversationState.value = data.conversation_state
    selectedGender.value = null
    selectedSkinTone.value = null
    selectedUndertone.value = null
    feedbackRating.value = 0
    feedbackComment.value = ''
    pushBot({ text: data.message, kind: 'gender' })
  } catch {
    pushBot({ text: 'Gagal memulai ulang sesi.' })
  } finally {
    loading.value = false
  }
}

// ── Profiling ─────────────────────────────────────────────────────────────────

async function pickGender(g) {
  if (loading.value) return
  selectedGender.value = g.id
  pushUser(g.label)
  await sendGender(g.code)
}

async function sendGender(code) {
  loading.value = true
  try {
    const data = await chatbotApi.setGender(sessionId.value, code)
    conversationState.value = data.conversation_state
    const kind = botKindForState(data)
    changingTarget.value = null
    pushBot({
      text: data.message,
      quick_replies: data.quick_replies,
      kind,
      summary: data.summary,
    })
  } catch (err) {
    pushBot({
      text: err.body?.detail?.message || 'Pilihan koleksi tidak valid.',
      kind: 'gender',
    })
  } finally {
    loading.value = false
  }
}

async function pickSkinTone(f) {
  if (loading.value) return
  selectedSkinTone.value = f.code
  if (changingTarget.value !== 'SKIN_TONE') selectedUndertone.value = null
  pushUser(`${f.name} (Fitzpatrick ${f.code})`)
  await sendSkinTone(f.code)
}

async function pickUndertone(u) {
  if (loading.value) return
  selectedUndertone.value = u.id
  pushUser(u.cap)
  await sendUndertone(u.code)
}

async function sendSkinTone(code) {
  loading.value = true
  try {
    const data = await chatbotApi.setSkinTone(sessionId.value, code)
    conversationState.value = data.conversation_state
    if (changingTarget.value === 'SKIN_TONE' && selectedUndertone.value) {
      // Only skin tone changed — auto-resend existing undertone to reach confirmation directly
      const existing = UNDERTONE_DATA.find(u => u.id === selectedUndertone.value)
      changingTarget.value = null
      if (existing) { await sendUndertone(existing.code); return }
    }
    changingTarget.value = null
    pushBot({ text: data.message, kind: 'undertone' })
  } catch (err) {
    changingTarget.value = null
    pushBot({ text: err.body?.detail?.message || 'Pilihan skin tone tidak valid.', kind: 'fitz' })
  } finally {
    loading.value = false
  }
}

async function sendUndertone(code) {
  loading.value = true
  try {
    const data = await chatbotApi.setUndertone(sessionId.value, code)
    conversationState.value = data.conversation_state
    pushBot({ text: data.message, quick_replies: data.quick_replies, kind: 'summary', summary: data.summary })
  } catch (err) {
    pushBot({
      text: err.body?.detail?.message || 'Pilihan undertone tidak valid.',
      kind: 'undertone',
    })
  } finally {
    loading.value = false
  }
}

async function doConfirm(isConfirmed, changeTarget = null) {
  loading.value = true
  let productsMessageIndex = null
  try {
    const data = await chatbotApi.confirm(sessionId.value, { isConfirmed, changeTarget, topN: 5 })
    conversationState.value = data.conversation_state
    if (isConfirmed && data.seasonal_result) {
      pushBot(
        { text: data.message, kind: 'seasonal', seasonal: data.seasonal_result },
        { scroll: false },
      )
      productsMessageIndex = pushBot(
        { kind: 'products', items: data.recommendation.items, quick_replies: data.quick_replies },
        { scroll: false },
      )
    } else {
      const state = data.conversation_state
      if (state === 'WAITING_GENDER') {
        selectedGender.value = null
        changingTarget.value = changeTarget
        pushBot({ text: data.message, kind: 'gender' })
      } else if (state === 'WAITING_SKIN_TONE' || state === 'WAITING_CHANGE_SELECTION') {
        selectedSkinTone.value = null
        if (changeTarget !== 'SKIN_TONE') selectedUndertone.value = null
        changingTarget.value = changeTarget
        pushBot({ text: data.message, kind: 'fitz' })
      } else if (state === 'WAITING_UNDERTONE') {
        selectedUndertone.value = null
        changingTarget.value = changeTarget
        pushBot({ text: data.message, kind: 'undertone' })
      } else {
        pushBot({ text: data.message, quick_replies: data.quick_replies })
      }
    }
  } catch {
    pushBot({ text: 'Terjadi kesalahan saat memproses rekomendasi.' })
  } finally {
    loading.value = false
    if (Number.isInteger(productsMessageIndex)) scrollToMessage(productsMessageIndex)
  }
}

// ── Recommendation actions ────────────────────────────────────────────────────

async function applyFilter(criteria) {
  loading.value = true
  try {
    const data = await chatbotApi.filter(sessionId.value, criteria)
    pushBot({ text: data.message, kind: 'products', items: data.items, quick_replies: data.quick_replies })
  } catch {
    pushBot({ text: 'Filter tidak dapat diterapkan.' })
  } finally {
    loading.value = false
  }
}

async function requestColorsToAvoid() {
  loading.value = true
  try {
    const data = await chatbotApi.colorsToAvoid(sessionId.value)
    pushBot({ text: data.message, kind: 'avoid', colors: data.colors_to_avoid, quick_replies: data.quick_replies })
  } catch {
    pushBot({ text: 'Gagal mengambil daftar warna yang dihindari.' })
  } finally {
    loading.value = false
  }
}

// ── Education ─────────────────────────────────────────────────────────────────

async function openEducationTopics(promptIndex = null) {
  loading.value = true
  const shouldAnchorPrompt = Number.isInteger(promptIndex)
  try {
    const data = await chatbotApi.listEducationTopics(sessionId.value)
    data.topics.forEach((t) => EDUCATION_TOPIC_CODES.add(t.code))
    const quickReplies = data.topics.map((t) => ({ label: t.title, value: t.code }))
    quickReplies.push({ label: 'Mulai rekomendasi', value: 'START_RECOMMENDATION' })
    conversationState.value = 'EDUCATION'
    pushBot(
      { text: 'Pilih topik personal color yang ingin Anda pelajari:', quick_replies: quickReplies },
      { scroll: !shouldAnchorPrompt },
    )
  } catch {
    pushBot({ text: 'Gagal memuat daftar edukasi.' }, { scroll: !shouldAnchorPrompt })
  } finally {
    loading.value = false
    if (shouldAnchorPrompt) scrollToMessage(promptIndex)
  }
}

async function openEducationContent(code, promptIndex = null) {
  loading.value = true
  const shouldAnchorPrompt = Number.isInteger(promptIndex)
  try {
    const data = await chatbotApi.getEducationTopic(code, sessionId.value)
    conversationState.value = 'EDUCATION'
    data.quick_replies?.forEach((qr) => {
      if (qr.value && !RESERVED_QUICK_REPLY_VALUES.has(qr.value)) {
        EDUCATION_TOPIC_CODES.add(qr.value)
      }
    })
    pushBot({
      kind: 'education',
      education: buildEducationContent(data),
      quick_replies: data.quick_replies,
    }, { scroll: !shouldAnchorPrompt })
  } catch (err) {
    pushBot({ text: err.body?.detail?.message || 'Topik edukasi tidak tersedia.' }, { scroll: !shouldAnchorPrompt })
  } finally {
    loading.value = false
    if (shouldAnchorPrompt) scrollToMessage(promptIndex)
  }
}

// ── Feedback ──────────────────────────────────────────────────────────────────

function openFeedback() { pushBot({ kind: 'feedback' }) }

async function submitFeedback(isSkipped) {
  if (!sessionId.value) return
  loading.value = true
  try {
    await chatbotApi.submitFeedback(sessionId.value, {
      rating: isSkipped ? null : (feedbackRating.value || null),
      comment: isSkipped ? null : feedbackComment.value || null,
      is_skipped: isSkipped,
    })
    pushBot({
      text: 'Terima kasih atas umpan balik Anda. Klik tombol di pojok kanan bawah untuk memulai sesi baru.',
      quick_replies: [{ label: 'Mulai sesi baru', value: 'START_PROFILING', primary: true }],
    })
    sessionId.value = null
    conversationState.value = null
  } catch {
    pushBot({ text: 'Gagal mengirim feedback.' })
  } finally {
    loading.value = false
  }
}

// ── Quick reply dispatcher ────────────────────────────────────────────────────

async function handleQuickReply(qr) {
  if (!qr) return
  const value = qr.value
  const label = qr.label
  const shouldAnchorEducationPrompt =
    value === 'EDUCATION' ||
    EDUCATION_TOPIC_CODES.has(value) ||
    (conversationState.value === 'EDUCATION' && !RESERVED_QUICK_REPLY_VALUES.has(value))
  const promptIndex = pushUser(label, { scroll: !shouldAnchorEducationPrompt })

  if (value === 'START_PROFILING') return startConversation()
  if (value === 'EDUCATION') return openEducationTopics(promptIndex)
  if (value === 'START_RECOMMENDATION') {
    conversationState.value = 'WAITING_GENDER'
    return restartProfiling()
  }
  if (EDUCATION_TOPIC_CODES.has(value) || (conversationState.value === 'EDUCATION' && !RESERVED_QUICK_REPLY_VALUES.has(value))) {
    return openEducationContent(value, promptIndex)
  }
  if (value === 'COLORS_TO_AVOID') return requestColorsToAvoid()
  if (value === 'FEEDBACK') return openFeedback()
  if (value === 'FILTER_PRICE_ASC') return applyFilter('PRICE_ASC')
  if (value === 'FILTER_RATING_DESC') return applyFilter('RATING_DESC')
  if (value === 'FILTER_POPULARITY_DESC') return applyFilter('POPULARITY_DESC')

  const state = conversationState.value
  if (state === 'WAITING_GENDER') return sendGender(value)
  if (state === 'WAITING_CHANGE_SELECTION') {
    if (value === 'CHANGE_GENDER') return doConfirm(false, 'GENDER')
    if (value === 'CHANGE_SKIN_TONE') return doConfirm(false, 'SKIN_TONE')
    if (value === 'CHANGE_UNDERTONE') return doConfirm(false, 'UNDERTONE')
  }
  if (state === 'WAITING_SKIN_TONE') {
    return sendSkinTone(value)
  }
  if (state === 'WAITING_UNDERTONE') return sendUndertone(value)
  if (state === 'WAITING_CONFIRMATION') {
    if (value === 'CONFIRM') return doConfirm(true)
    if (value === 'CHANGE_GENDER') return doConfirm(false, 'GENDER')
    if (value === 'CHANGE_SKIN_TONE') return doConfirm(false, 'SKIN_TONE')
    if (value === 'CHANGE_UNDERTONE') return doConfirm(false, 'UNDERTONE')
  }
}

// ── Free text ─────────────────────────────────────────────────────────────────

async function sendFreeText() {
  const text = composer.value.trim()
  if (!text) return
  composer.value = ''
  pushUser(text)

  if (!sessionId.value) { await startConversation(); return }

  loading.value = true
  try {
    const data = await chatbotApi.freeText(sessionId.value, text)
    if (data.conversation_state) conversationState.value = data.conversation_state
    if (data.seasonal_result) {
      pushBot({ text: data.message, kind: 'seasonal', seasonal: data.seasonal_result })
      pushBot({ kind: 'products', items: data.recommendation.items, quick_replies: data.quick_replies })
    } else if (data.message) {
      const kind = botKindForState(data)
      pushBot({
        text: data.message,
        quick_replies: data.quick_replies,
        kind,
        summary: data.summary,
      })
    }
  } catch (err) {
    pushBot({ text: err.body?.detail?.message || 'Maaf, saya belum memahami pesan tersebut.' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.seera-chatbot {
  --seera-bg: #f7f2ec;
  --seera-bg-elev: #fbf7f2;
  --seera-card: #ffffff;
  --seera-ink: #1f1b16;
  --seera-ink-2: #4a4239;
  --seera-ink-3: #8a7f72;
  --seera-line: #e8dfd3;
  --seera-line-2: #dcd0bf;
  --seera-clay: #c97b5c;
  --seera-clay-deep: #a85e40;
  --seera-sage: #8fa68a;
  --seera-radius: 18px;
  --seera-radius-sm: 12px;
  --seera-shadow: 0 24px 48px rgba(31, 27, 22, 0.18), 0 4px 12px rgba(31, 27, 22, 0.1);
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
  color: var(--seera-ink);
}

.seera-chatbot * { box-sizing: border-box; }

/* ── Launcher ──────────────────────────────────────────────────────────────── */

.seera-chatbot__launcher {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 18px 12px 14px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, var(--seera-clay), var(--seera-clay-deep));
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 12px 28px rgba(168, 94, 64, 0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}
.seera-chatbot__launcher:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px rgba(168, 94, 64, 0.4);
}
.seera-chatbot__launcher.is-open {
  width: 44px; height: 44px;
  padding: 0; justify-content: center; border-radius: 50%;
}
.seera-chatbot__launcher-icon { display: inline-flex; align-items: center; justify-content: center; }

/* ── Window ────────────────────────────────────────────────────────────────── */

.seera-chatbot__window {
  position: absolute;
  bottom: 64px; right: 0;
  width: min(380px, calc(100vw - 32px));
  height: min(620px, calc(100vh - 100px));
  background: var(--seera-bg);
  border: 1px solid var(--seera-line);
  border-radius: var(--seera-radius);
  box-shadow: var(--seera-shadow);
  display: flex; flex-direction: column;
  overflow: hidden;
}

/* ── Header ────────────────────────────────────────────────────────────────── */

.seera-chatbot__header {
  padding: 14px 16px;
  border-bottom: 1px solid var(--seera-line);
  display: flex; align-items: center; justify-content: space-between;
  background: var(--seera-bg);
}
.seera-chatbot__head-left { display: flex; align-items: center; gap: 10px; }
.seera-chatbot__avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background:
    radial-gradient(circle at 30% 25%, #ffe4d2, transparent 50%),
    radial-gradient(circle at 70% 70%, #c97b5c, transparent 60%),
    linear-gradient(135deg, #f2c9b4, #a85e40);
  position: relative;
}
.seera-chatbot__avatar::after {
  content: '';
  position: absolute; bottom: 0; right: 0;
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--seera-sage); border: 2px solid var(--seera-bg);
}
.seera-chatbot__title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 16px; font-weight: 500; line-height: 1;
}
.seera-chatbot__subtitle { font-size: 11px; color: var(--seera-ink-3); margin-top: 2px; }
.seera-chatbot__head-actions { display: flex; gap: 6px; }
.seera-chatbot__icon-btn {
  width: 30px; height: 30px; border-radius: 10px;
  border: 1px solid var(--seera-line);
  background: var(--seera-bg-elev); color: var(--seera-ink-2);
  display: grid; place-items: center; cursor: pointer; transition: background 0.15s;
}
.seera-chatbot__icon-btn:hover { background: #fff; }

/* ── Messages ──────────────────────────────────────────────────────────────── */

.seera-chatbot__messages {
  flex: 1; overflow-y: auto;
  padding: 16px 14px 12px;
  display: flex; flex-direction: column; gap: 12px;
  scroll-behavior: smooth;
}
.seera-chatbot__day {
  text-align: center; font-size: 10px; color: var(--seera-ink-3);
  text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px;
}
.seera-chatbot__row { display: flex; gap: 8px; align-items: flex-end; }
.seera-chatbot__row.is-user { flex-direction: row-reverse; }
.seera-chatbot__row-avatar {
  width: 22px; height: 22px; border-radius: 50%;
  background: linear-gradient(135deg, #f2c9b4, #a85e40); flex-shrink: 0;
}
.seera-chatbot__row-stack {
  display: flex; flex-direction: column; gap: 6px;
  max-width: 85%;
}
.seera-chatbot__row-stack--wide { max-width: 93%; }
.seera-chatbot__row.is-user .seera-chatbot__row-stack { align-items: flex-end; }

/* ── Bubbles ───────────────────────────────────────────────────────────────── */

.seera-chatbot__bubble {
  padding: 10px 14px;
  background: #fff; border: 1px solid var(--seera-line);
  border-radius: 16px 16px 16px 4px;
  font-size: 13.5px; line-height: 1.5; color: var(--seera-ink);
}
.seera-chatbot__bubble--user {
  background: var(--seera-ink); color: var(--seera-bg);
  border-color: var(--seera-ink); border-radius: 16px 16px 4px 16px;
}
.seera-chatbot__bubble--education {
  width: 100%;
  padding: 12px 12px 13px;
  background: #fffdf9;
  border-color: var(--seera-line-2);
  box-shadow: 0 1px 0 rgba(31, 27, 22, 0.03);
}
.seera-education__eyebrow {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--seera-clay-deep);
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: 3px;
}
.seera-education__title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 15.5px;
  font-weight: 500;
  line-height: 1.25;
  margin-bottom: 8px;
}
.seera-education__text,
.seera-education__note,
.seera-education__step-body {
  font-size: 12.5px;
  line-height: 1.48;
  color: var(--seera-ink-2);
}
.seera-education__steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}
.seera-education__cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
  gap: 8px;
  margin-top: 12px;
}
.seera-education__card {
  min-height: 104px;
  background: var(--education-card-bg, var(--seera-bg-elev));
  border: 1px solid var(--seera-line-2);
  border-top: 3px solid var(--education-card-accent, var(--seera-clay));
  border-radius: 12px;
  padding: 10px 10px 11px;
  box-shadow: 0 1px 2px rgba(31, 27, 22, 0.04);
}
.seera-education__card-head {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  margin-bottom: 7px;
}
.seera-education__card-swatch {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  background: var(--education-card-accent, var(--seera-clay));
  border: 1px solid rgba(31, 27, 22, 0.12);
  flex: 0 0 auto;
}
.seera-education__card-title {
  min-width: 0;
  color: var(--seera-ink);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.seera-education__card-body {
  color: var(--seera-ink-2);
  font-size: 11.5px;
  line-height: 1.42;
}
.seera-education__step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-height: 74px;
  background: linear-gradient(180deg, #fffaf5 0%, var(--seera-bg-elev) 100%);
  border: 1px solid #e5d6c5;
  border-left: 3px solid rgba(201, 123, 92, 0.55);
  border-radius: 12px;
  padding: 11px 11px 11px 10px;
  box-shadow: 0 1px 2px rgba(31, 27, 22, 0.04);
}
.seera-education__step-num {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #f4dfd3;
  border: 1px solid rgba(201, 123, 92, 0.34);
  color: var(--seera-clay-deep);
  display: grid;
  place-items: center;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 13px;
  font-weight: 600;
  line-height: 1;
  flex: 0 0 auto;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
}
.seera-education__step-copy { min-width: 0; }
.seera-education__step-title {
  font-weight: 700;
  font-size: 12.5px;
  line-height: 1.3;
  color: var(--seera-ink);
  margin-bottom: 5px;
}
.seera-education__note {
  margin-top: 10px;
  padding-top: 9px;
  border-top: 1px dashed var(--seera-line-2);
}

/* ── Blocks (shared) ───────────────────────────────────────────────────────── */

.seera-chatbot__block {
  background: #fff; border: 1px solid var(--seera-line);
  border-radius: var(--seera-radius-sm);
  padding: 12px 14px; font-size: 12.5px;
}
.seera-chatbot__block-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 10px;
}
.seera-chatbot__block-tag {
  font-size: 9.5px; text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--seera-ink-3); font-family: 'JetBrains Mono', monospace;
}
.seera-chatbot__block-title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 15px; font-weight: 500; margin-top: 2px; letter-spacing: -0.01em;
}
.seera-chatbot__block-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.seera-chatbot__chip {
  font-size: 9.5px; color: var(--seera-ink-3); font-family: 'JetBrains Mono', monospace;
}

/* ── Fitzpatrick block ─────────────────────────────────────────────────────── */

.seera-fitz {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 5px;
  margin-top: 10px;
}
.seera-fitz__cell {
  aspect-ratio: 1 / 1.3;
  border-radius: 8px;
  position: relative;
  cursor: pointer;
  display: flex; flex-direction: column; justify-content: flex-end;
  padding: 4px;
  border: 2px solid transparent;
  transition: all 0.2s;
  user-select: none;
}
.seera-fitz__cell:hover:not(.seera-fitz__cell--disabled) { transform: translateY(-2px); }
.seera-fitz__cell--selected {
  border-color: var(--seera-ink);
  box-shadow: 0 0 0 3px rgba(31, 27, 22, 0.1);
}
.seera-fitz__cell--disabled { cursor: default; }
.seera-fitz__num {
  font-family: 'Fraunces', Georgia, serif;
  font-weight: 500; font-size: 13px;
  background: rgba(255, 255, 255, 0.9);
  width: 18px; height: 18px; border-radius: 50%;
  display: grid; place-items: center;
  color: var(--seera-ink); line-height: 1;
}
.seera-fitz__labels {
  display: grid; grid-template-columns: repeat(6, 1fr);
  gap: 5px; margin-top: 6px;
}
.seera-fitz__label {
  font-size: 8px; color: var(--seera-ink-3);
  text-align: center; line-height: 1.25;
  font-family: 'JetBrains Mono', monospace;
  display: flex; flex-direction: column; align-items: center;
}

/* ── Gender / collection preference block ─────────────────────────────────── */

.seera-gender {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px; margin-top: 10px;
}
.seera-gender__card {
  min-height: 78px;
  background: var(--seera-bg-elev);
  border: 1px solid var(--seera-line-2);
  border-radius: 12px;
  padding: 12px 8px;
  display: flex; flex-direction: column; justify-content: center; gap: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}
.seera-gender__card:hover:not(.seera-gender__card--disabled) {
  border-color: var(--seera-ink-3);
  transform: translateY(-2px);
}
.seera-gender__card--selected {
  border-color: var(--seera-ink);
  box-shadow: 0 0 0 3px rgba(31, 27, 22, 0.08);
}
.seera-gender__card--disabled { cursor: default; }
.seera-gender__cap {
  font-size: 12px; font-weight: 700; color: var(--seera-ink);
}
.seera-gender__hint {
  font-size: 10px; color: var(--seera-ink-3); line-height: 1.25;
}

/* ── Undertone block ───────────────────────────────────────────────────────── */

.seera-undertone {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 8px; margin-top: 10px; margin-bottom: 8px;
}
.seera-undertone__card {
  background: linear-gradient(180deg, #f5dcc9, #e8c2a8);
  border-radius: 12px;
  padding: 16px 10px 14px;
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  user-select: none;
}
.seera-undertone__card:hover:not(.seera-undertone__card--disabled) { transform: translateY(-2px); }
.seera-undertone__card--selected { border-color: var(--seera-ink); }
.seera-undertone__card--disabled { cursor: default; }
.seera-undertone__label {
  font-size: 11px; font-weight: 500;
  color: var(--seera-ink); margin-bottom: 4px;
  line-height: 1.3;
}
.seera-undertone__cap {
  font-size: 10px; color: var(--seera-ink-2);
  text-transform: uppercase; letter-spacing: 0.08em;
}
.seera-undertone__hint {
  font-size: 11px; color: var(--seera-ink-3); text-align: center;
}

/* ── Summary block ─────────────────────────────────────────────────────────── */

.seera-chatbot__summary { display: flex; flex-direction: column; gap: 4px; font-size: 12.5px; }

/* ── Seasonal block (gaya AIML PaletteBlock) ───────────────────────────────── */

.seera-chatbot__seasonal-membership {
  display: flex; flex-direction: column; gap: 6px; margin-top: 10px;
}
.seera-chatbot__seasonal-row {
  display: grid; grid-template-columns: 58px 1fr 36px;
  gap: 8px; align-items: center; font-size: 11.5px;
}
.seera-chatbot__bar {
  background: var(--seera-line); border-radius: 99px;
  height: 6px; overflow: hidden; position: relative;
}
.seera-chatbot__bar-fill {
  display: block; height: 100%;
  background: linear-gradient(90deg, var(--seera-clay), var(--seera-clay-deep));
  border-radius: 99px;
  transition: width 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.seera-chatbot__bar-value {
  font-family: 'JetBrains Mono', monospace; font-size: 10.5px;
  text-align: right;
}
.seera-chatbot__palette-foot {
  font-size: 11.5px; color: var(--seera-ink-3);
  display: flex; align-items: center; gap: 7px;
  margin-top: 10px; padding-top: 10px;
  border-top: 1px dashed var(--seera-line-2);
}
.seera-chatbot__palette-dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0; display: inline-block;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

/* ── Product block ─────────────────────────────────────────────────────────── */

.seera-chatbot__products { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.seera-chatbot__product {
  background: var(--seera-bg-elev); border: 1px solid var(--seera-line);
  border-radius: 12px; overflow: hidden;
  transition: border-color 0.18s, box-shadow 0.18s, transform 0.18s;
}
.seera-chatbot__product:hover,
.seera-chatbot__product:focus-within {
  border-color: var(--seera-line-2);
  box-shadow: 0 8px 18px rgba(31, 27, 22, 0.1);
  transform: translateY(-2px);
}
.seera-chatbot__product-thumb {
  aspect-ratio: 4 / 5;
  position: relative;
  overflow: hidden;
}
.seera-chatbot__product-thumb::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(31, 27, 22, 0.02) 30%, rgba(31, 27, 22, 0.5) 100%);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s;
}
.seera-chatbot__product:hover .seera-chatbot__product-thumb::after,
.seera-chatbot__product:focus-within .seera-chatbot__product-thumb::after {
  opacity: 1;
}
.seera-chatbot__product-score {
  position: absolute; top: 6px; right: 6px;
  background: rgba(31, 27, 22, 0.92); color: var(--seera-bg);
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  padding: 3px 6px; border-radius: 6px;
  z-index: 2;
}
.seera-chatbot__product-score em {
  font-family: 'Fraunces', serif; font-style: normal;
  font-size: 11px; margin-right: 1px;
}
.seera-chatbot__product-rank {
  position: absolute; top: 6px; left: 6px;
  background: rgba(255, 255, 255, 0.92); color: var(--seera-ink);
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  padding: 3px 6px; border-radius: 6px;
  z-index: 2;
}
.seera-chatbot__product-action {
  position: absolute;
  left: 8px;
  right: 8px;
  bottom: 8px;
  min-height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.78);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.96);
  color: var(--seera-ink);
  cursor: pointer;
  font-family: inherit;
  font-size: 11.5px;
  font-weight: 700;
  line-height: 1.2;
  padding: 8px 10px;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.18s, transform 0.18s, background 0.18s, color 0.18s;
  z-index: 3;
}
.seera-chatbot__product:hover .seera-chatbot__product-action,
.seera-chatbot__product:focus-within .seera-chatbot__product-action {
  opacity: 1;
  transform: translateY(0);
}
.seera-chatbot__product-action:hover,
.seera-chatbot__product-action:focus-visible {
  background: var(--seera-ink);
  color: var(--seera-bg);
  outline: none;
}
.seera-chatbot__product-action:focus-visible {
  box-shadow: 0 0 0 3px rgba(255, 253, 249, 0.72);
}
.seera-chatbot__product-info { padding: 8px 10px 10px; }
.seera-chatbot__product-title { font-size: 11.5px; font-weight: 500; line-height: 1.3; }
.seera-chatbot__product-meta {
  display: flex; justify-content: space-between;
  margin-top: 4px; font-size: 10.5px; color: var(--seera-ink-2);
}
.seera-chatbot__product-price { font-family: 'JetBrains Mono', monospace; }
.seera-chatbot__product-rating { color: var(--seera-clay-deep); font-weight: 500; }
.seera-chatbot__product-label { font-size: 10px; color: var(--seera-ink-3); margin-top: 2px; }
.seera-chatbot__product-swatches { display: flex; gap: 4px; margin-top: 6px; }
.seera-chatbot__swatch-dot {
  width: 12px; height: 12px; border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.08); display: inline-block;
}

/* ── Colors to avoid ───────────────────────────────────────────────────────── */

.seera-chatbot__avoid-list { display: flex; flex-direction: column; gap: 8px; margin-top: 4px; }
.seera-chatbot__avoid-item { display: flex; gap: 10px; align-items: flex-start; }
.seera-chatbot__avoid-swatch {
  width: 28px; height: 28px; border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.06); flex-shrink: 0;
}
.seera-chatbot__avoid-name { font-size: 12.5px; font-weight: 500; }
.seera-chatbot__mono {
  font-family: 'JetBrains Mono', monospace; font-size: 10.5px;
  color: var(--seera-ink-3); margin-left: 4px;
}
.seera-chatbot__avoid-reason { font-size: 11px; color: var(--seera-ink-3); margin-top: 2px; }
.seera-chatbot__empty { font-size: 12px; color: var(--seera-ink-3); }

/* ── Feedback block ────────────────────────────────────────────────────────── */

.seera-chatbot__feedback { display: flex; gap: 4px; margin: 8px 0; }
.seera-chatbot__star {
  background: none; border: none; font-size: 22px;
  cursor: pointer; color: #d8cab8; padding: 0;
}
.seera-chatbot__star.active { color: var(--seera-clay); }
.seera-chatbot__feedback-text {
  width: 100%; border: 1px solid var(--seera-line);
  border-radius: 10px; padding: 8px 10px;
  font-family: inherit; font-size: 12.5px; resize: none;
  margin-bottom: 8px; background: var(--seera-bg-elev);
}
.seera-chatbot__feedback-actions { display: flex; gap: 6px; }

/* ── Quick replies ─────────────────────────────────────────────────────────── */

.seera-chatbot__quick-replies { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 2px; }
.seera-chatbot__qr {
  background: var(--seera-bg-elev); border: 1px solid var(--seera-line-2);
  color: var(--seera-ink); padding: 6px 12px; border-radius: 999px;
  font-size: 12px; cursor: pointer; font-family: inherit; transition: all 0.15s;
}
.seera-chatbot__qr:hover { background: var(--seera-ink); color: var(--seera-bg); border-color: var(--seera-ink); }
.seera-chatbot__qr:disabled {
  cursor: default;
  opacity: 0.55;
}
.seera-chatbot__qr:disabled:hover {
  background: var(--seera-bg-elev);
  color: var(--seera-ink);
  border-color: var(--seera-line-2);
}
.seera-chatbot__qr--primary { background: var(--seera-clay); color: #fff; border-color: var(--seera-clay); }
.seera-chatbot__qr--primary:hover { background: var(--seera-clay-deep); border-color: var(--seera-clay-deep); }

/* ── Typing indicator ──────────────────────────────────────────────────────── */

.seera-chatbot__typing {
  display: inline-flex; gap: 4px; padding: 10px 14px;
  background: #fff; border: 1px solid var(--seera-line);
  border-radius: 16px 16px 16px 4px; width: fit-content;
}
.seera-chatbot__typing span {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--seera-ink-3);
  animation: seera-bounce 1.2s infinite;
}
.seera-chatbot__typing span:nth-child(2) { animation-delay: 0.15s; }
.seera-chatbot__typing span:nth-child(3) { animation-delay: 0.3s; }
@keyframes seera-bounce {
  0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
  40% { opacity: 1; transform: translateY(-3px); }
}

/* ── Composer ──────────────────────────────────────────────────────────────── */

.seera-chatbot__composer {
  display: flex; align-items: flex-end; gap: 8px;
  border-top: 1px solid var(--seera-line);
  padding: 10px 12px; background: var(--seera-bg);
}
.seera-chatbot__composer textarea {
  flex: 1; resize: none; font-family: inherit; font-size: 13px;
  padding: 8px 10px; border: 1px solid var(--seera-line);
  border-radius: 12px; background: var(--seera-bg-elev);
  max-height: 80px; outline: none; line-height: 1.4;
}
.seera-chatbot__composer textarea:focus { border-color: var(--seera-clay); }
.seera-chatbot__send {
  border: none; width: 36px; height: 36px; border-radius: 50%;
  background: var(--seera-clay); color: #fff;
  display: grid; place-items: center; cursor: pointer;
  transition: background 0.15s, transform 0.15s; flex-shrink: 0;
}
.seera-chatbot__send:hover:not(:disabled) { background: var(--seera-clay-deep); transform: translateY(-1px); }
.seera-chatbot__send:disabled { background: var(--seera-line-2); cursor: not-allowed; }

/* ── Transition ────────────────────────────────────────────────────────────── */

.seera-fade-enter-from,
.seera-fade-leave-to { opacity: 0; transform: translateY(8px); }
.seera-fade-enter-active,
.seera-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }

@media (hover: none) {
  .seera-chatbot__product-thumb::after {
    opacity: 1;
    background: linear-gradient(180deg, rgba(31, 27, 22, 0) 45%, rgba(31, 27, 22, 0.42) 100%);
  }
  .seera-chatbot__product-action {
    opacity: 1;
    transform: none;
  }
}

/* ── Responsive ────────────────────────────────────────────────────────────── */

@media (max-width: 480px) {
  .seera-chatbot { bottom: 16px; right: 16px; }
  .seera-chatbot__window {
    width: calc(100vw - 32px);
    height: calc(100vh - 90px);
    bottom: 64px;
  }
  .seera-chatbot__products { grid-template-columns: 1fr; }
}
</style>
