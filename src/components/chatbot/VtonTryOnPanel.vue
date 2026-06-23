<template>
  <div class="seera-vton">
    <div class="seera-vton__tag">REALISTIC VIRTUAL TRY-ON · {{ product.product_name }}</div>

    <!-- ═══ Tahap 1: Consent (FR-VTO-05) ═══ -->
    <div v-if="stage === 'consent'" class="seera-vton__section-box">
      <div class="seera-vton__title">Izin pemrosesan foto</div>
      <p class="seera-vton__text">
        Untuk membuat preview realistic try-on, kami memerlukan foto badan bagian atas Anda.
        Foto hanya diproses untuk sesi ini, <strong>tidak dipakai untuk mengenali identitas</strong>
        (face recognition), tidak dipakai untuk melatih model, dan dihapus otomatis setelah
        masa sesi berakhir.
      </p>
      <label class="seera-vton__consent">
        <input v-model="consentChecked" type="checkbox" />
        <span>Saya setuju foto saya diproses untuk preview try-on sesi ini.</span>
      </label>
      <div class="seera-vton__actions">
        <button
          type="button"
          class="seera-vton__btn seera-vton__btn--primary"
          :disabled="!consentChecked"
          @click="proceedFromConsent"
        >
          Lanjutkan
        </button>
        <button type="button" class="seera-vton__btn seera-vton__btn--ghost" @click="$emit('back')">
          Batal
        </button>
      </div>
    </div>

    <!-- ═══ Tahap experimental: konfirmasi aset seadanya (FR-VTO-16, UI 16.5) ═══ -->
    <div v-else-if="stage === 'experimental-confirm'" class="seera-vton__section-box">
      <div class="seera-vton__exp-badge">{{ experimentalLabel }}</div>
      <div class="seera-vton__title">Kualitas aset produk terbatas</div>
      <div class="seera-vton__exp-preview">
        <img :src="product.image_url" :alt="product.product_name" />
      </div>
      <div class="seera-vton__exp-name">
        {{ product.product_name }}
        <span v-if="variantColorName"> · {{ variantColorName }}</span>
      </div>
      <p class="seera-vton__text">
        Foto produk ini belum memenuhi standar aset virtual try-on, sehingga hasil
        preview AI dapat berbeda dari produk asli.
      </p>
      <div class="seera-vton__actions">
        <button type="button" class="seera-vton__btn seera-vton__btn--primary" @click="stage = 'capture'">
          Tetap Coba Preview
        </button>
        <button type="button" class="seera-vton__btn seera-vton__btn--ghost" @click="$emit('back')">
          Pilih Produk Lain
        </button>
      </div>
    </div>

    <!-- ═══ Tahap 2: Capture / upload upper-body (FR-VTO-03, UI 16.2) ═══ -->
    <div v-else-if="stage === 'capture'" class="seera-vton__section-box">
      <div class="seera-vton__stage">
        <video
          v-show="cameraState === 'active'"
          ref="videoEl"
          autoplay
          playsinline
          muted
          class="seera-vton__video"
        />
        <div v-if="cameraState !== 'active'" class="seera-vton__placeholder">
          <p v-if="cameraState === 'starting'">Menyalakan kamera…</p>
          <template v-else>
            <p>Kamera tidak tersedia atau izin ditolak.</p>
            <p class="seera-vton__placeholder-sub">Anda tetap bisa mengunggah foto dari galeri.</p>
          </template>
        </div>
        <!-- Body guide: kepala, bahu, torso, batas pinggang -->
        <svg
          v-if="cameraState === 'active'"
          class="seera-vton__guide"
          :class="{ 'seera-vton__guide--ok': positioned }"
          viewBox="0 0 100 130"
          preserveAspectRatio="xMidYMid meet"
          aria-hidden="true"
        >
          <ellipse cx="50" cy="22" rx="13" ry="16" fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="1.4" stroke-dasharray="4 3" />
          <path d="M30 48 Q50 38 70 48 L74 70 Q74 96 70 104 L30 104 Q26 96 26 70 Z"
            fill="none" stroke="rgba(255,255,255,0.85)" stroke-width="1.4" stroke-dasharray="4 3" />
          <line x1="20" y1="104" x2="80" y2="104" stroke="rgba(255,255,255,0.6)" stroke-width="1.2" stroke-dasharray="3 3" />
          <text x="50" y="112" text-anchor="middle" fill="rgba(255,255,255,0.75)" font-size="4.5">batas pinggang</text>
        </svg>
        <!-- Countdown auto-capture saat posisi sudah sesuai -->
        <div v-if="cameraState === 'active' && countdown" class="seera-vton__countdown">{{ countdown }}</div>
        <!-- Panduan posisi langsung di kamera -->
        <div
          v-if="cameraState === 'active' && guideMessage && !countdown"
          class="seera-vton__guide-msg"
          :class="{ 'is-ok': positioned }"
        >
          {{ guideMessage }}
        </div>
      </div>

      <p class="seera-vton__hint">
        {{ autoCaptureSupported
          ? 'Posisikan wajah, bahu, dan pakaian bagian atas di dalam panduan. Foto akan diambil otomatis saat posisi sudah pas.'
          : 'Pastikan wajah, bahu, dan pakaian bagian atas terlihat jelas, lalu foto akan diambil otomatis saat Anda diam menghadap kamera.' }}
      </p>
      <p v-if="captureError" class="seera-vton__error">{{ captureError }}</p>

      <div class="seera-vton__actions">
        <button
          type="button"
          class="seera-vton__btn"
          :disabled="busy || cameraState !== 'active'"
          @click="captureFromCamera"
        >
          Ambil Manual
        </button>
        <button type="button" class="seera-vton__btn" :disabled="busy" @click="fileInput && fileInput.click()">
          Unggah Foto
        </button>
        <button type="button" class="seera-vton__btn seera-vton__btn--ghost" :disabled="busy" @click="$emit('back')">
          Batal
        </button>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept="image/jpeg,image/jpg,image/png"
        class="seera-vton__file"
        @change="onFileSelected"
      />
    </div>

    <!-- ═══ Tahap 3: Processing (FR-VTO-10, UI 16.3) ═══ -->
    <div v-else-if="stage === 'processing'" class="seera-vton__section-box seera-vton__processing">
      <div class="seera-vton__spinner" aria-hidden="true" />
      <div class="seera-vton__title">Sedang membuat realistic try-on preview…</div>
      <p class="seera-vton__text">
        Model {{ modelLabel }} sedang memproses foto Anda dengan produk
        "{{ product.product_name }}". Proses ini dapat memakan waktu hingga beberapa menit.
      </p>
      <div class="seera-vton__actions">
        <button type="button" class="seera-vton__btn seera-vton__btn--ghost" @click="cancelProcessing">
          Batalkan
        </button>
      </div>
    </div>

    <!-- ═══ Tahap 4: Hasil (FR-VTO-11/12, UI 16.4) ═══ -->
    <div v-else-if="stage === 'result'" class="seera-vton__section-box">
      <div v-if="experimentalResultLabel" class="seera-vton__exp-badge seera-vton__exp-badge--result">
        {{ experimentalResultLabel }}
      </div>
      <!-- Side-by-side 3 kolom: produk asli + garment VTON + hasil (BR-VTO-17/26) -->
      <div class="seera-vton__compare seera-vton__compare--triple">
        <div class="seera-vton__compare-col">
          <div class="seera-vton__compare-label">Produk Asli</div>
          <div class="seera-vton__compare-frame">
            <img v-if="productImageUrl" class="seera-vton__compare-img" :src="productImageUrl" alt="Foto produk asli" />
          </div>
        </div>
        <div class="seera-vton__compare-col">
          <div class="seera-vton__compare-label">Garment VTON</div>
          <div class="seera-vton__compare-frame">
            <img v-if="garmentImageUrl" class="seera-vton__compare-img" :src="garmentImageUrl" alt="Gambar garment VTON" />
          </div>
        </div>
        <div class="seera-vton__compare-col">
          <div class="seera-vton__compare-label">Hasil Try-On</div>
          <div class="seera-vton__compare-frame" :style="{ background: resultBackdrop }">
            <img class="seera-vton__compare-img" :src="outputUrl" alt="Hasil realistic try-on" />
          </div>
        </div>
      </div>
      <div class="seera-vton__result-meta">
        <strong>{{ product.product_name }}</strong>
        <span v-if="variantColorName" class="seera-vton__variant-chip">{{ variantColorName }}</span>
        <span class="seera-vton__model-chip">{{ modelLabel }}</span>
      </div>
      <p class="seera-vton__disclaimer">
        Hasil virtual try-on adalah visualisasi AI dan dapat berbeda dari produk asli.
        Ini preview visual, bukan jaminan ukuran, fitting, atau kenyamanan pakaian.
      </p>

      <!-- Coba produk lain (tanpa mengulang dari awal) -->
      <div v-if="otherProducts.length" class="seera-vton__section">Coba produk lain</div>
      <div v-if="otherProducts.length" class="seera-vton__products">
        <button
          v-for="p in otherProducts"
          :key="p.product_id"
          type="button"
          class="seera-vton__product-pick"
          :disabled="busy"
          :title="p.product_name"
          @click="tryAnotherProduct(p)"
        >
          <span class="seera-vton__pick-thumb" :style="{ background: thumbFor(p) }" />
          <span class="seera-vton__pick-rank">#{{ p.rank }}</span>
        </button>
      </div>

      <!-- Background preset (FR-VTO-12) -->
      <div v-if="backgrounds.length" class="seera-vton__section">Latar belakang</div>
      <div v-if="backgrounds.length" class="seera-vton__backgrounds">
        <button
          v-for="bg in backgrounds"
          :key="bg.background_id"
          type="button"
          class="seera-vton__bg-pick"
          :class="{ 'is-selected': selectedBackground && bg.background_id === selectedBackground.background_id }"
          :title="bg.background_name"
          @click="selectedBackground = bg"
        >
          <span class="seera-vton__bg-swatch" :style="{ background: bg.image_url }" />
          <span class="seera-vton__bg-name">{{ bg.background_name }}</span>
        </button>
      </div>

      <div class="seera-vton__actions">
        <button type="button" class="seera-vton__btn" @click="$emit('back')">
          Kembali ke rekomendasi
        </button>
        <button
          v-if="!feedbackSent"
          type="button"
          class="seera-vton__btn seera-vton__btn--primary"
          @click="stage = 'feedback'"
        >
          Beri umpan balik
        </button>
      </div>
    </div>

    <!-- ═══ Tahap 5: Feedback kualitas try-on (FR-VTO-13) ═══ -->
    <div v-else-if="stage === 'feedback'" class="seera-vton__section-box">
      <div class="seera-vton__title">Bagaimana hasil try-on ini?</div>
      <div v-for="dim in FEEDBACK_DIMENSIONS" :key="dim.key" class="seera-vton__rating-row">
        <span class="seera-vton__rating-label">{{ dim.label }}</span>
        <span class="seera-vton__stars">
          <button
            v-for="n in 5"
            :key="n"
            type="button"
            class="seera-vton__star"
            :class="{ active: ratings[dim.key] >= n }"
            @click="ratings[dim.key] = n"
            :aria-label="`${dim.label} ${n}`"
          >★</button>
        </span>
      </div>
      <textarea
        v-model="feedbackComment"
        rows="2"
        placeholder="Komentar (opsional)"
        class="seera-vton__comment"
      />
      <div class="seera-vton__actions">
        <button
          type="button"
          class="seera-vton__btn seera-vton__btn--primary"
          :disabled="busy"
          @click="submitFeedback"
        >
          Kirim
        </button>
        <button type="button" class="seera-vton__btn seera-vton__btn--ghost" :disabled="busy" @click="stage = 'result'">
          Lewati
        </button>
      </div>
    </div>

    <!-- ═══ Tahap gagal (FR-VTO-14, alur 8.3) ═══ -->
    <div v-else-if="stage === 'failed'" class="seera-vton__section-box">
      <div class="seera-vton__title">Try-on belum berhasil</div>
      <p class="seera-vton__error">{{ failureMessage }}</p>
      <p class="seera-vton__text">
        Rekomendasi produk Anda tetap berlaku — kegagalan try-on tidak memengaruhi hasil rekomendasi.
      </p>
      <div class="seera-vton__actions">
        <button
          v-if="failureAllowsRetake"
          type="button"
          class="seera-vton__btn seera-vton__btn--primary"
          @click="retakePhoto"
        >
          Ambil ulang foto
        </button>
        <button type="button" class="seera-vton__btn" @click="$emit('back')">
          Kembali ke rekomendasi
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { chatbotApi } from '../../api/chatbot'

const props = defineProps({
  sessionId: { type: [Number, String], required: true },
  initialProduct: { type: Object, required: true },
  products: { type: Array, default: () => [] }, // item rekomendasi vton_ready
  backgrounds: { type: Array, default: () => [] }
})

const emit = defineEmits(['back'])

const FEEDBACK_DIMENSIONS = [
  { key: 'visual_quality_rating', label: 'Kualitas visual' },
  { key: 'proportion_rating', label: 'Proporsi tubuh & pakaian' },
  { key: 'garment_similarity_rating', label: 'Kemiripan dengan produk' },
  { key: 'satisfaction_rating', label: 'Kepuasan umum' }
]

const POLL_INTERVAL_MS = 2500
const POLL_MAX_MS = 6 * 60 * 1000

// ── State ──
const stage = ref('consent') // consent | capture | processing | result | feedback | failed
const product = ref(props.initialProduct)
const consentChecked = ref(false)
const busy = ref(false)
const captureError = ref('')
const failureMessage = ref('')
const failureAllowsRetake = ref(false)
const personImageId = ref(null)
const jobId = ref(null)
const outputUrl = ref(null)
const productImageUrl = ref(null)
const garmentImageUrl = ref(null)
const qualityMode = ref(null)
const modelLabel = ref('IDM-VTON')
const selectedBackground = ref(null)
const feedbackSent = ref(false)
const feedbackComment = ref('')
const ratings = reactive({
  visual_quality_rating: 0,
  proportion_rating: 0,
  garment_similarity_rating: 0,
  satisfaction_rating: 0
})

const videoEl = ref(null)
const fileInput = ref(null)
const cameraState = ref('idle')
// ── Auto-capture (deteksi posisi) ──
const autoCaptureSupported = ref(typeof window !== 'undefined' && 'FaceDetector' in window)
const guideMessage = ref('')
const positioned = ref(false)
const countdown = ref(null)
let mediaStream = null
let faceDetector = null
let detectTimer = null
let countdownTimer = null
let stableFrames = 0
let captured = false
// Fallback stabilitas (tanpa FaceDetector)
let diffCanvas = null
let prevFrameData = null
let stillFrames = 0
let pollTimer = null
let pollStartedAt = 0

const otherProducts = computed(() =>
  props.products.filter((p) => p.product_id !== product.value.product_id && p.vton_supported)
)

const resultBackdrop = computed(
  () => selectedBackground.value?.image_url || 'linear-gradient(180deg, #FFFFFF 0%, #ECECEC 100%)'
)

// Tier experimental/limited memerlukan konfirmasi sebelum inference (FR-VTO-16)
const needsExperimentalConfirm = computed(() =>
  ['vton_experimental', 'vton_limited'].includes(product.value?.vton_asset_tier)
)
const experimentalLabel = computed(() =>
  product.value?.vton_asset_tier === 'vton_limited' ? 'Kualitas Aset Terbatas' : 'Preview Eksperimental'
)
const variantColorName = computed(() => {
  const colors = product.value?.colors || []
  const dominant = colors.find((c) => c.color_role === 'DOMINANT') || colors[0]
  return dominant?.color_name || null
})

function proceedFromConsent() {
  stage.value = needsExperimentalConfirm.value ? 'experimental-confirm' : 'capture'
}

const experimentalResultLabel = computed(() => {
  if (qualityMode.value === 'experimental') return 'Preview Eksperimental'
  if (qualityMode.value === 'limited') return 'Kualitas Aset Terbatas'
  return null
})

// ── Kamera ──

watch(stage, async (next, prev) => {
  if (next === 'capture') {
    await nextTick()
    startCamera()
  } else if (prev === 'capture') {
    stopCamera()
  }
})

onMounted(() => {
  if (stage.value === 'capture') startCamera()
})

onBeforeUnmount(() => {
  stopCamera()
  stopPolling()
})

async function startCamera() {
  if (cameraState.value === 'active') return
  cameraState.value = 'starting'
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraState.value = 'unavailable'
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 960 }, height: { ideal: 1280 } },
      audio: false
    })
    if (videoEl.value) {
      videoEl.value.srcObject = mediaStream
      cameraState.value = 'active'
      captured = false
      startAutoCapture()
    } else {
      stopCamera()
      cameraState.value = 'unavailable'
    }
  } catch {
    cameraState.value = 'unavailable'
  }
}

function stopCamera() {
  stopAutoCapture()
  if (mediaStream) {
    mediaStream.getTracks().forEach((t) => t.stop())
    mediaStream = null
  }
  if (cameraState.value === 'active') cameraState.value = 'idle'
}

function captureFromCamera() {
  const video = videoEl.value
  if (!video || !video.videoWidth || captured) return
  captured = true
  stopAutoCapture()
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  canvas.toBlob(
    (blob) => {
      if (!blob) return
      uploadPersonImage(new File([blob], 'badan.jpg', { type: 'image/jpeg' }), 'CAMERA')
    },
    'image/jpeg',
    0.92
  )
}

// ── Auto-capture: ambil foto otomatis saat posisi sesuai panduan ──

const DETECT_INTERVAL_MS = 250
const STABLE_FRAMES_REQUIRED = 3   // ~0.75s posisi konsisten sebelum hitung mundur
const STILL_FRAMES_REQUIRED = 8    // fallback: ~2s diam

function startAutoCapture() {
  stopAutoCapture()
  captured = false
  stableFrames = 0
  stillFrames = 0
  prevFrameData = null
  if (autoCaptureSupported.value) {
    try {
      faceDetector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 3 })
    } catch {
      faceDetector = null
      autoCaptureSupported.value = false
    }
  }
  guideMessage.value = 'Posisikan wajah dan bahu di dalam panduan'
  detectTimer = setInterval(detectStep, DETECT_INTERVAL_MS)
}

function stopAutoCapture() {
  if (detectTimer) { clearInterval(detectTimer); detectTimer = null }
  cancelCountdown()
  positioned.value = false
  faceDetector = null
}

function cancelCountdown() {
  if (countdownTimer) { clearInterval(countdownTimer); countdownTimer = null }
  countdown.value = null
}

async function detectStep() {
  const video = videoEl.value
  if (captured || busy.value || stage.value !== 'capture' || cameraState.value !== 'active'
      || !video || !video.videoWidth) {
    return
  }
  // Saat hitung mundur berjalan, cukup pastikan posisi masih oke.
  if (countdown.value) {
    const stillOk = autoCaptureSupported.value ? await evaluateFace(video) : evaluateStillness(video)
    if (!stillOk) {
      cancelCountdown()
      stableFrames = 0
    }
    return
  }

  const ok = autoCaptureSupported.value ? await evaluateFace(video) : evaluateStillness(video)
  positioned.value = ok
  if (ok) {
    stableFrames += 1
    const need = autoCaptureSupported.value ? STABLE_FRAMES_REQUIRED : STILL_FRAMES_REQUIRED
    if (stableFrames >= need) startCountdown()
  } else {
    stableFrames = 0
  }
}

// FaceDetector: posisi wajah harus di area panduan & ukuran wajar (bukan close-up wajah)
async function evaluateFace(video) {
  if (!faceDetector) return false
  let faces = []
  try {
    faces = await faceDetector.detect(video)
  } catch {
    return false
  }
  const vw = video.videoWidth
  const vh = video.videoHeight
  if (!faces.length) {
    guideMessage.value = 'Wajah belum terdeteksi — masuk ke dalam panduan'
    return false
  }
  if (faces.length > 1) {
    guideMessage.value = 'Pastikan hanya satu orang di kamera'
    return false
  }
  const box = faces[0].boundingBox
  const cx = (box.x + box.width / 2) / vw
  const cy = (box.y + box.height / 2) / vh
  const wFrac = box.width / vw
  const hFrac = box.height / vh
  // Batas atas = close-up wajah saja (ditolak, VTON butuh tubuh). Batas bawah
  // dibuat longgar agar framing kepala–pinggang (wajah kecil di atas) ikut lolos
  // sesuai panduan tubuh di layar, bukan hanya wajah+dada.
  if (wFrac > 0.42 || hFrac > 0.5) {
    guideMessage.value = 'Mundur sedikit dari kamera'
    return false
  }
  if (wFrac < 0.08) {
    guideMessage.value = 'Mendekat sedikit ke kamera'
    return false
  }
  if (cx < 0.30 || cx > 0.70) {
    guideMessage.value = 'Posisikan wajah di tengah panduan'
    return false
  }
  if (cy < 0.06 || cy > 0.45) {
    guideMessage.value = cy > 0.45 ? 'Naikkan kamera sedikit' : 'Turunkan kamera sedikit'
    return false
  }
  guideMessage.value = 'Posisi pas — tahan sebentar'
  return true
}

// Fallback tanpa FaceDetector: deteksi pengguna diam + pencahayaan cukup
function evaluateStillness(video) {
  if (!diffCanvas) {
    diffCanvas = document.createElement('canvas')
    diffCanvas.width = 64
    diffCanvas.height = 48
  }
  const ctx = diffCanvas.getContext('2d', { willReadFrequently: true })
  ctx.drawImage(video, 0, 0, 64, 48)
  const frame = ctx.getImageData(0, 0, 64, 48).data
  let brightness = 0
  for (let i = 0; i < frame.length; i += 4) {
    brightness += 0.299 * frame[i] + 0.587 * frame[i + 1] + 0.114 * frame[i + 2]
  }
  brightness /= frame.length / 4
  if (brightness < 45) {
    guideMessage.value = 'Pencahayaan kurang — cari tempat lebih terang'
    prevFrameData = frame
    return false
  }
  if (!prevFrameData) {
    prevFrameData = frame
    guideMessage.value = 'Tahan posisi menghadap kamera'
    return false
  }
  let diff = 0
  for (let i = 0; i < frame.length; i += 4) {
    diff += Math.abs(frame[i] - prevFrameData[i])
  }
  diff /= frame.length / 4
  prevFrameData = frame
  if (diff < 8) {
    guideMessage.value = 'Posisi stabil — tahan sebentar'
    return true
  }
  guideMessage.value = 'Tahan posisi menghadap kamera'
  return false
}

function startCountdown() {
  if (countdownTimer) return
  countdown.value = 3
  countdownTimer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      cancelCountdown()
      captureFromCamera()
    }
  }, 700)
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (file) uploadPersonImage(file, 'UPLOAD')
}

// ── Upload + validasi person image (FR-VTO-04) ──

async function uploadPersonImage(file, sourceType) {
  busy.value = true
  captureError.value = ''
  try {
    const data = await chatbotApi.uploadVtonPersonImage(
      props.sessionId, file, sourceType, true
    )
    if (!data.person_image_id) {
      captureError.value = data.message || 'Foto tidak valid. Silakan coba lagi.'
      // Re-arm auto-capture agar pengguna bisa langsung mencoba ulang
      if (stage.value === 'capture' && cameraState.value === 'active') {
        captured = false
        startAutoCapture()
      }
      return
    }
    personImageId.value = data.person_image_id
    await startJob()
  } catch (err) {
    captureError.value = err.body?.detail?.message || 'Gagal mengunggah foto. Silakan coba lagi.'
    if (stage.value === 'capture' && cameraState.value === 'active') {
      captured = false
      startAutoCapture()
    }
  } finally {
    busy.value = false
  }
}

// ── Job lifecycle (FR-VTO-09/10) ──

async function startJob() {
  stopCamera()
  stage.value = 'processing'
  try {
    const dominant = (product.value?.colors || []).find((c) => c.color_role === 'DOMINANT')
    const data = await chatbotApi.createVtonJob(props.sessionId, {
      productId: product.value.product_id,
      personImageId: personImageId.value,
      backgroundId: selectedBackground.value?.background_id ?? null,
      variantId: dominant?.color_id ?? null,
      // Tier experimental/limited sudah dikonfirmasi pengguna di tahap sebelumnya
      confirmExperimental: needsExperimentalConfirm.value
    })
    jobId.value = data.vton_job_id
    if (data.tryon_quality_mode) qualityMode.value = data.tryon_quality_mode
    startPolling()
  } catch (err) {
    showFailure(err.body?.detail?.message || 'Gagal memulai try-on.', false)
  }
}

function startPolling() {
  stopPolling()
  pollStartedAt = Date.now()
  pollTimer = setInterval(pollJob, POLL_INTERVAL_MS)
  pollJob()
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollJob() {
  if (!jobId.value) return
  if (Date.now() - pollStartedAt > POLL_MAX_MS) {
    stopPolling()
    showFailure('Proses try-on melebihi batas waktu. Silakan coba lagi nanti.', true)
    return
  }
  try {
    const data = await chatbotApi.getVtonJob(jobId.value)
    if (data.model_name) modelLabel.value = data.model_name
    if (data.product_image_url) productImageUrl.value = data.product_image_url
    if (data.tryon_quality_mode) qualityMode.value = data.tryon_quality_mode
    if (data.garment_vton_image_url) {
      garmentImageUrl.value = chatbotApi.apiBase
        ? chatbotApi.apiBase + data.garment_vton_image_url
        : data.garment_vton_image_url
    }
    if (data.status === 'SUCCESS' && data.output_image_url) {
      stopPolling()
      outputUrl.value = chatbotApi.apiBase
        ? chatbotApi.apiBase + data.output_image_url
        : data.output_image_url
      stage.value = 'result'
    } else if (data.status === 'FAILED' || data.status === 'EXPIRED') {
      stopPolling()
      showFailure(data.error_message || 'Try-on gagal diproses.', true)
    }
  } catch {
    // biarkan polling berikutnya mencoba lagi
  }
}

function cancelProcessing() {
  stopPolling()
  emit('back')
}

function showFailure(message, allowRetake) {
  failureMessage.value = message
  failureAllowsRetake.value = allowRetake
  stage.value = 'failed'
}

function retakePhoto() {
  captureError.value = ''
  personImageId.value = null
  stage.value = 'capture'
}

// ── Coba produk lain (alur 18.2 no. 5) ──

async function tryAnotherProduct(p) {
  product.value = p
  feedbackSent.value = false
  garmentImageUrl.value = null
  // Tier experimental/limited untuk produk baru wajib konfirmasi ulang (FR-VTO-16)
  if (needsExperimentalConfirm.value) {
    stage.value = 'experimental-confirm'
    return
  }
  if (personImageId.value) {
    await startJob()
  } else {
    stage.value = 'capture'
  }
}

// ── Feedback (FR-VTO-13) ──

async function submitFeedback() {
  if (!jobId.value) return
  busy.value = true
  try {
    await chatbotApi.submitVtonFeedback(jobId.value, {
      visual_quality_rating: ratings.visual_quality_rating || null,
      proportion_rating: ratings.proportion_rating || null,
      garment_similarity_rating: ratings.garment_similarity_rating || null,
      satisfaction_rating: ratings.satisfaction_rating || null,
      comment: feedbackComment.value || null
    })
    feedbackSent.value = true
    stage.value = 'result'
  } catch (err) {
    captureError.value = err.body?.detail?.message || 'Gagal mengirim feedback.'
    stage.value = 'result'
  } finally {
    busy.value = false
  }
}

// ── Util ──

function thumbFor(p) {
  const imageUrl = p.image_url
  if (imageUrl) {
    if (/^(linear-gradient|radial-gradient|url\()/i.test(imageUrl)) return imageUrl
    return `url("${String(imageUrl).replace(/"/g, '\\"')}") center / cover no-repeat`
  }
  const colors = (p.colors || []).map((c) => c.hex_code).slice(0, 3)
  return colors.length
    ? `linear-gradient(160deg, ${colors.join(',')})`
    : 'linear-gradient(160deg, #F2C9B4, #C97B5C)'
}
</script>

<style scoped>
.seera-vton {
  width: 100%;
  background: #fff;
  border: 1px solid var(--seera-line, #e8dfd3);
  border-radius: 14px;
  padding: 12px;
}
.seera-vton__tag {
  font-size: 9px;
  letter-spacing: 0.12em;
  color: var(--seera-clay-deep, #a85e40);
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: 8px;
  text-transform: uppercase;
}
.seera-vton__title {
  font-size: 14px;
  font-weight: 700;
  color: var(--seera-ink, #1f1b16);
  margin-bottom: 6px;
}
.seera-vton__text {
  font-size: 12px;
  line-height: 1.5;
  color: var(--seera-ink-2, #4a4239);
  margin: 0 0 8px;
}
.seera-vton__consent {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  font-size: 12px;
  color: var(--seera-ink, #1f1b16);
  background: var(--seera-bg-elev, #fbf7f2);
  border: 1px solid var(--seera-line-2, #dcd0bf);
  border-radius: 10px;
  padding: 9px 10px;
  cursor: pointer;
  margin-bottom: 10px;
}
.seera-vton__consent input { margin-top: 2px; }
.seera-vton__stage {
  position: relative;
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 10px;
  overflow: hidden;
  background: #1f1b16;
}
.seera-vton__video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }
.seera-vton__guide { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; transition: filter 0.2s; }
.seera-vton__guide--ok { filter: drop-shadow(0 0 6px rgba(143, 166, 138, 0.9)); }
.seera-vton__guide--ok ellipse,
.seera-vton__guide--ok path { stroke: #8fa68a !important; }
.seera-vton__countdown {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Fraunces', Georgia, serif;
  font-size: 84px;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 4px 18px rgba(0, 0, 0, 0.6);
  pointer-events: none;
  animation: seera-vton-pop 0.7s ease;
}
@keyframes seera-vton-pop {
  0% { transform: scale(1.5); opacity: 0.2; }
  100% { transform: scale(1); opacity: 1; }
}
.seera-vton__guide-msg {
  position: absolute;
  left: 50%;
  bottom: 10px;
  transform: translateX(-50%);
  max-width: 90%;
  text-align: center;
  font-size: 11.5px;
  font-weight: 600;
  color: #fff;
  background: rgba(31, 27, 22, 0.62);
  border-radius: 999px;
  padding: 5px 12px;
  pointer-events: none;
}
.seera-vton__guide-msg.is-ok { background: rgba(96, 122, 90, 0.85); }
.seera-vton__placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #f7f2ec;
  font-size: 12.5px;
  text-align: center;
  padding: 16px;
}
.seera-vton__placeholder-sub { color: rgba(247, 242, 236, 0.7); font-size: 11.5px; }
.seera-vton__hint {
  margin: 8px 2px 0;
  font-size: 11.5px;
  line-height: 1.45;
  color: var(--seera-ink-2, #4a4239);
}
.seera-vton__error {
  margin: 8px 2px;
  padding: 8px 10px;
  border-radius: 10px;
  background: #fdf1ec;
  border: 1px solid #ecc7b8;
  font-size: 11.5px;
  line-height: 1.45;
  color: #94432a;
}
.seera-vton__actions { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.seera-vton__btn {
  border: 1px solid var(--seera-line-2, #dcd0bf);
  background: var(--seera-bg-elev, #fbf7f2);
  color: var(--seera-ink, #1f1b16);
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}
.seera-vton__btn:disabled { opacity: 0.5; cursor: not-allowed; }
.seera-vton__btn--primary {
  background: linear-gradient(135deg, var(--seera-clay, #c97b5c), var(--seera-clay-deep, #a85e40));
  border-color: transparent;
  color: #fff;
}
.seera-vton__btn--ghost { background: transparent; }
.seera-vton__file { display: none; }
.seera-vton__processing { text-align: center; padding: 18px 8px; }
.seera-vton__processing .seera-vton__actions { justify-content: center; }
.seera-vton__spinner {
  width: 34px;
  height: 34px;
  margin: 0 auto 12px;
  border-radius: 50%;
  border: 3px solid var(--seera-line, #e8dfd3);
  border-top-color: var(--seera-clay-deep, #a85e40);
  animation: seera-vton-spin 0.9s linear infinite;
}
@keyframes seera-vton-spin { to { transform: rotate(360deg); } }
.seera-vton__result-frame {
  width: 100%;
  border-radius: 12px;
  border: 1px solid var(--seera-line, #e8dfd3);
  display: flex;
  justify-content: center;
  padding: 12px;
}
.seera-vton__result-img {
  max-width: 100%;
  max-height: 360px;
  border-radius: 8px;
  box-shadow: 0 10px 24px rgba(31, 27, 22, 0.22);
}
/* Side-by-side garment fidelity verification (BR-VTO-17/26) */
.seera-vton__compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.seera-vton__compare--triple { grid-template-columns: 1fr 1fr 1fr; }
.seera-vton__exp-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #8a5a16;
  background: #fdf2dc;
  border: 1px solid #e9cf9b;
  border-radius: 999px;
  padding: 3px 10px;
  margin-bottom: 8px;
}
.seera-vton__exp-badge--result { margin-bottom: 6px; }
.seera-vton__exp-preview {
  width: 100%;
  max-width: 180px;
  margin: 6px auto;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--seera-line, #e8dfd3);
}
.seera-vton__exp-preview img { width: 100%; display: block; }
.seera-vton__exp-name {
  text-align: center;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--seera-ink, #1f1b16);
  margin-bottom: 6px;
}
.seera-vton__variant-chip {
  font-size: 10px;
  background: var(--seera-bg, #f7f2ec);
  border: 1px solid var(--seera-line-2, #dcd0bf);
  border-radius: 999px;
  padding: 2px 8px;
  color: var(--seera-ink-2, #4a4239);
}
.seera-vton__compare-col { display: flex; flex-direction: column; gap: 4px; }
.seera-vton__compare-label {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--seera-ink-3, #8a7f72);
  text-align: center;
}
.seera-vton__compare-frame {
  border-radius: 10px;
  border: 1px solid var(--seera-line, #e8dfd3);
  aspect-ratio: 3 / 4;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--seera-bg-elev, #fbf7f2);
}
.seera-vton__compare-img { width: 100%; height: 100%; object-fit: contain; }
.seera-vton__result-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 8px;
  font-size: 13px;
  color: var(--seera-ink, #1f1b16);
}
.seera-vton__model-chip {
  font-size: 9.5px;
  font-family: 'JetBrains Mono', monospace;
  background: var(--seera-bg, #f7f2ec);
  border: 1px solid var(--seera-line-2, #dcd0bf);
  border-radius: 999px;
  padding: 2px 8px;
  color: var(--seera-ink-3, #8a7f72);
}
.seera-vton__disclaimer {
  margin: 6px 2px 0;
  font-size: 10.5px;
  line-height: 1.4;
  color: var(--seera-ink-3, #8a7f72);
}
.seera-vton__section {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--seera-ink-3, #8a7f72);
  margin: 12px 0 6px;
}
.seera-vton__products { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 2px; }
.seera-vton__product-pick {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 10px;
  border: 2px solid transparent;
  padding: 0;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
  background: none;
}
.seera-vton__product-pick:hover { border-color: var(--seera-clay, #c97b5c); }
.seera-vton__product-pick:disabled { opacity: 0.6; cursor: not-allowed; }
.seera-vton__pick-thumb { position: absolute; inset: 0; }
.seera-vton__pick-rank {
  position: absolute;
  left: 3px;
  bottom: 3px;
  background: rgba(31, 27, 22, 0.72);
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  border-radius: 5px;
  padding: 1px 4px;
}
.seera-vton__backgrounds { display: flex; gap: 6px; flex-wrap: wrap; }
.seera-vton__bg-pick {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  width: 52px;
}
.seera-vton__bg-swatch {
  width: 44px;
  height: 30px;
  border-radius: 8px;
  border: 2px solid transparent;
  box-shadow: inset 0 0 0 1px rgba(31, 27, 22, 0.08);
}
.seera-vton__bg-pick.is-selected .seera-vton__bg-swatch { border-color: var(--seera-clay-deep, #a85e40); }
.seera-vton__bg-name { font-size: 9px; color: var(--seera-ink-2, #4a4239); text-align: center; line-height: 1.2; }
.seera-vton__rating-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin: 6px 0;
}
.seera-vton__rating-label { font-size: 12px; color: var(--seera-ink-2, #4a4239); }
.seera-vton__stars { display: inline-flex; gap: 2px; }
.seera-vton__star {
  background: none;
  border: none;
  font-size: 17px;
  color: var(--seera-line-2, #dcd0bf);
  cursor: pointer;
  padding: 0 1px;
}
.seera-vton__star.active { color: #e3a008; }
.seera-vton__comment {
  width: 100%;
  border: 1px solid var(--seera-line-2, #dcd0bf);
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 12px;
  font-family: inherit;
  resize: vertical;
  margin-top: 6px;
}
</style>
