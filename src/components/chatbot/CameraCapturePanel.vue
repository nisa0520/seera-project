<template>
  <div class="seera-camera">
    <div class="seera-camera__stage">
      <video
        v-show="cameraState === 'active'"
        ref="videoEl"
        autoplay
        playsinline
        muted
        class="seera-camera__video"
      />
      <div v-if="cameraState !== 'active'" class="seera-camera__placeholder">
        <p v-if="cameraState === 'starting'">Menyalakan kamera…</p>
        <template v-else>
          <p>Kamera tidak tersedia atau izin ditolak.</p>
          <p class="seera-camera__placeholder-sub">Anda tetap bisa mengunggah foto dari galeri.</p>
        </template>
      </div>

      <!-- Face guide / placeholder kepala (FR-IMG-03) -->
      <svg
        v-if="cameraState === 'active'"
        class="seera-camera__guide"
        viewBox="0 0 100 100"
        preserveAspectRatio="xMidYMid meet"
        aria-hidden="true"
      >
        <ellipse
          cx="50" cy="44" rx="24" ry="32"
          fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="1.6"
          stroke-dasharray="4 3"
        />
        <path
          d="M26 92 Q50 70 74 92"
          fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="1.4"
          stroke-dasharray="4 3"
        />
      </svg>
    </div>

    <p class="seera-camera__hint">
      Posisikan wajah di dalam garis panduan, pencahayaan cukup, tanpa filter kamera.
    </p>
    <p class="seera-camera__privacy">
      Foto hanya dipakai untuk analisis warna kulit pada sesi ini dan tidak disimpan permanen.
    </p>

    <div class="seera-camera__actions">
      <button
        type="button"
        class="seera-camera__btn seera-camera__btn--primary"
        :disabled="disabled || cameraState !== 'active'"
        @click="capture"
      >
        Ambil Foto
      </button>
      <button
        type="button"
        class="seera-camera__btn"
        :disabled="disabled"
        @click="fileInput && fileInput.click()"
      >
        Unggah Foto
      </button>
      <button
        type="button"
        class="seera-camera__btn seera-camera__btn--ghost"
        :disabled="disabled"
        @click="$emit('manual')"
      >
        Input Manual
      </button>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/jpg,image/png"
      class="seera-camera__file"
      @change="onFileSelected"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

defineProps({
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['captured', 'manual'])

const videoEl = ref(null)
const fileInput = ref(null)
const cameraState = ref('starting') // starting | active | unavailable
let mediaStream = null

onMounted(async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraState.value = 'unavailable'
    return
  }
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 720 }, height: { ideal: 720 } },
      audio: false
    })
    if (videoEl.value) {
      videoEl.value.srcObject = mediaStream
      cameraState.value = 'active'
    } else {
      stopCamera()
      cameraState.value = 'unavailable'
    }
  } catch {
    cameraState.value = 'unavailable'
  }
})

onBeforeUnmount(stopCamera)

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((t) => t.stop())
    mediaStream = null
  }
}

function capture() {
  const video = videoEl.value
  if (!video || !video.videoWidth) return
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  canvas.toBlob(
    (blob) => {
      if (!blob) return
      const file = new File([blob], 'wajah.jpg', { type: 'image/jpeg' })
      emit('captured', { file, sourceType: 'CAMERA' })
    },
    'image/jpeg',
    0.92
  )
}

function onFileSelected(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  emit('captured', { file, sourceType: 'UPLOAD' })
}
</script>

<style scoped>
.seera-camera {
  width: 100%;
  background: #fff;
  border: 1px solid var(--seera-line, #e8dfd3);
  border-radius: 14px;
  padding: 10px;
}
.seera-camera__stage {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 10px;
  overflow: hidden;
  background: #1f1b16;
}
.seera-camera__video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}
.seera-camera__guide {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
.seera-camera__placeholder {
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
.seera-camera__placeholder-sub {
  color: rgba(247, 242, 236, 0.7);
  font-size: 11.5px;
}
.seera-camera__hint {
  margin: 8px 2px 0;
  font-size: 11.5px;
  line-height: 1.45;
  color: var(--seera-ink-2, #4a4239);
}
.seera-camera__privacy {
  margin: 4px 2px 0;
  font-size: 10.5px;
  line-height: 1.4;
  color: var(--seera-ink-3, #8a7f72);
}
.seera-camera__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.seera-camera__btn {
  border: 1px solid var(--seera-line-2, #dcd0bf);
  background: var(--seera-bg-elev, #fbf7f2);
  color: var(--seera-ink, #1f1b16);
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.seera-camera__btn:hover:not(:disabled) { background: #fff; }
.seera-camera__btn:disabled { opacity: 0.5; cursor: not-allowed; }
.seera-camera__btn--primary {
  background: linear-gradient(135deg, var(--seera-clay, #c97b5c), var(--seera-clay-deep, #a85e40));
  border-color: transparent;
  color: #fff;
}
.seera-camera__btn--ghost { background: transparent; }
.seera-camera__file { display: none; }
</style>
