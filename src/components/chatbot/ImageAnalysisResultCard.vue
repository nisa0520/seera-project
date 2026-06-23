<template>
  <div class="seera-imgresult">
    <div class="seera-imgresult__head">
      <div v-if="faceCrop" class="seera-imgresult__crop">
        <img :src="faceCrop" alt="Crop wajah Anda" />
      </div>
      <div class="seera-imgresult__summary">
        <div class="seera-imgresult__row">
          <span class="seera-imgresult__label">Skin tone</span>
          <span class="seera-imgresult__value">
            <span class="seera-imgresult__swatch" :style="{ background: sampleHex || '#d4a382' }" />
            {{ result.skin_tone.name }} (Tipe {{ result.skin_tone.code }})
          </span>
        </div>
        <div class="seera-imgresult__row">
          <span class="seera-imgresult__label">Undertone</span>
          <span class="seera-imgresult__value">{{ result.undertone.name }}</span>
        </div>
      </div>
    </div>

    <div class="seera-imgresult__confidences">
      <div class="seera-imgresult__conf">
        <div class="seera-imgresult__conf-head">
          <span>Keyakinan skin tone</span><span>{{ pct(result.skin_tone.confidence) }}%</span>
        </div>
        <div class="seera-imgresult__bar">
          <div class="seera-imgresult__bar-fill" :style="{ width: pct(result.skin_tone.confidence) + '%' }" />
        </div>
      </div>
      <div class="seera-imgresult__conf">
        <div class="seera-imgresult__conf-head">
          <span>Keyakinan undertone</span><span>{{ pct(result.undertone.confidence) }}%</span>
        </div>
        <div class="seera-imgresult__bar">
          <div class="seera-imgresult__bar-fill" :style="{ width: pct(result.undertone.confidence) + '%' }" />
        </div>
      </div>
    </div>

    <div v-if="result.low_confidence" class="seera-imgresult__warning">
      Tingkat keyakinan deteksi cukup rendah. Pencahayaan, filter, atau makeup dapat
      memengaruhi hasil — silakan periksa kembali atau ubah hasil secara manual.
    </div>

    <!-- Mode ubah hasil (FR-IMG-08: "Ubah Hasil") -->
    <div v-if="adjusting" class="seera-imgresult__adjust">
      <div class="seera-imgresult__adjust-title">Skin tone (Fitzpatrick)</div>
      <div class="seera-imgresult__fitz">
        <button
          v-for="f in FITZPATRICK"
          :key="f.code"
          type="button"
          class="seera-imgresult__fitz-cell"
          :class="{ 'is-selected': selectedSkin === f.code }"
          :style="{ background: f.hex }"
          :aria-label="`${f.name} — Tipe ${f.code}`"
          @click="selectedSkin = f.code"
        >
          {{ f.code }}
        </button>
      </div>
      <div class="seera-imgresult__adjust-title">Undertone</div>
      <div class="seera-imgresult__undertone">
        <button
          v-for="u in UNDERTONES"
          :key="u.code"
          type="button"
          class="seera-imgresult__chip"
          :class="{ 'is-selected': selectedUndertone === u.code }"
          @click="selectedUndertone = u.code"
        >
          {{ u.label }}
        </button>
      </div>
    </div>

    <div class="seera-imgresult__actions">
      <button
        type="button"
        class="seera-imgresult__btn seera-imgresult__btn--primary"
        :disabled="disabled"
        @click="confirm"
      >
        {{ adjusting ? 'Gunakan Hasil Ini' : 'Lanjutkan' }}
      </button>
      <button
        v-if="!adjusting"
        type="button"
        class="seera-imgresult__btn"
        :disabled="disabled"
        @click="adjusting = true"
      >
        Ubah Hasil
      </button>
      <button
        type="button"
        class="seera-imgresult__btn seera-imgresult__btn--ghost"
        :disabled="disabled"
        @click="$emit('retake')"
      >
        Ambil Ulang Foto
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  result: { type: Object, required: true },
  faceCrop: { type: String, default: null },
  sampleHex: { type: String, default: null },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'retake'])

const FITZPATRICK = [
  { code: 'I', name: 'Very Fair', hex: '#F5DBC4' },
  { code: 'II', name: 'Fair', hex: '#EAC2A0' },
  { code: 'III', name: 'Medium Fair', hex: '#D4A382' },
  { code: 'IV', name: 'Moderate Brown', hex: '#A87858' },
  { code: 'V', name: 'Brown', hex: '#7A4F36' },
  { code: 'VI', name: 'Dark Brown', hex: '#4A2E20' }
]

const UNDERTONES = [
  { code: 'COOL', label: 'Cool' },
  { code: 'NEUTRAL', label: 'Neutral' },
  { code: 'WARM', label: 'Warm' }
]

const adjusting = ref(false)
const selectedSkin = ref(props.result.skin_tone.code)
const selectedUndertone = ref(props.result.undertone.code)

function pct(value) {
  return typeof value === 'number' ? Math.round(value * 100) : 0
}

function confirm() {
  const correctedSkinTone =
    selectedSkin.value !== props.result.skin_tone.code ? selectedSkin.value : null
  const correctedUndertone =
    selectedUndertone.value !== props.result.undertone.code ? selectedUndertone.value : null
  emit('confirm', { correctedSkinTone, correctedUndertone })
}
</script>

<style scoped>
.seera-imgresult {
  width: 100%;
  background: #fff;
  border: 1px solid var(--seera-line, #e8dfd3);
  border-radius: 14px;
  padding: 12px;
}
.seera-imgresult__head {
  display: flex;
  gap: 10px;
  align-items: center;
}
.seera-imgresult__crop {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--seera-line-2, #dcd0bf);
  flex-shrink: 0;
}
.seera-imgresult__crop img { width: 100%; height: 100%; object-fit: cover; }
.seera-imgresult__summary { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.seera-imgresult__row { display: flex; flex-direction: column; gap: 1px; }
.seera-imgresult__label {
  font-size: 9.5px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--seera-ink-3, #8a7f72);
}
.seera-imgresult__value {
  font-size: 13px;
  font-weight: 600;
  color: var(--seera-ink, #1f1b16);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.seera-imgresult__swatch {
  width: 14px;
  height: 14px;
  border-radius: 5px;
  border: 1px solid rgba(31, 27, 22, 0.15);
  display: inline-block;
}
.seera-imgresult__confidences {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 10px;
}
.seera-imgresult__conf-head {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--seera-ink-2, #4a4239);
  margin-bottom: 3px;
}
.seera-imgresult__bar {
  height: 6px;
  border-radius: 999px;
  background: var(--seera-bg, #f7f2ec);
  overflow: hidden;
}
.seera-imgresult__bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--seera-clay, #c97b5c), var(--seera-clay-deep, #a85e40));
}
.seera-imgresult__warning {
  margin-top: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  background: #fff7ef;
  border: 1px solid #ecd1b8;
  font-size: 11.5px;
  line-height: 1.45;
  color: #8a5a2e;
}
.seera-imgresult__adjust { margin-top: 12px; }
.seera-imgresult__adjust-title {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--seera-ink-3, #8a7f72);
  margin: 8px 0 5px;
}
.seera-imgresult__fitz { display: flex; gap: 4px; }
.seera-imgresult__fitz-cell {
  flex: 1;
  height: 34px;
  border-radius: 8px;
  border: 2px solid transparent;
  font-size: 10.5px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
  cursor: pointer;
}
.seera-imgresult__fitz-cell.is-selected {
  border-color: var(--seera-ink, #1f1b16);
}
.seera-imgresult__undertone { display: flex; gap: 6px; }
.seera-imgresult__chip {
  flex: 1;
  padding: 7px 0;
  border-radius: 999px;
  border: 1px solid var(--seera-line-2, #dcd0bf);
  background: var(--seera-bg-elev, #fbf7f2);
  font-size: 12px;
  font-weight: 600;
  color: var(--seera-ink, #1f1b16);
  cursor: pointer;
}
.seera-imgresult__chip.is-selected {
  background: var(--seera-ink, #1f1b16);
  border-color: var(--seera-ink, #1f1b16);
  color: #fff;
}
.seera-imgresult__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}
.seera-imgresult__btn {
  border: 1px solid var(--seera-line-2, #dcd0bf);
  background: var(--seera-bg-elev, #fbf7f2);
  color: var(--seera-ink, #1f1b16);
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}
.seera-imgresult__btn:disabled { opacity: 0.5; cursor: not-allowed; }
.seera-imgresult__btn--primary {
  background: linear-gradient(135deg, var(--seera-clay, #c97b5c), var(--seera-clay-deep, #a85e40));
  border-color: transparent;
  color: #fff;
}
.seera-imgresult__btn--ghost { background: transparent; }
</style>
