<template>
  <section class="pt-32 pb-20 px-6 md:px-16 bg-gray-50 dark:bg-gray-900 min-h-screen">
    <div class="max-w-6xl mx-auto grid lg:grid-cols-2 gap-8">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Seera Color Advisor</h1>
        <p class="text-sm text-gray-500 dark:text-gray-300 mt-2">
          Chatbot profiling skin tone & undertone untuk rekomendasi warna pakaian personal.
        </p>

        <div class="mt-6 h-[420px] overflow-y-auto space-y-3 border rounded-xl p-4 bg-gray-50 dark:bg-gray-900">
          <div
            v-for="(item, idx) in messages"
            :key="idx"
            :class="item.role === 'user' ? 'text-right' : 'text-left'"
          >
            <div
              :class="[
                'inline-block max-w-[85%] px-4 py-2 rounded-xl text-sm',
                item.role === 'user'
                  ? 'bg-[#b48b3c] text-black'
                  : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100 border border-gray-200 dark:border-gray-600'
              ]"
            >
              {{ item.text }}
            </div>
          </div>
        </div>

        <div class="mt-4 flex gap-2">
          <input
            v-model="inputMessage"
            @keyup.enter="handleSend"
            placeholder="Ketik jawaban (contoh: 2, cool, atau tanya seasonal)"
            class="flex-1 border border-gray-300 dark:border-gray-600 rounded-xl px-4 py-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
          <button
            @click="handleSend"
            :disabled="sending"
            class="px-4 py-3 rounded-xl bg-[#b48b3c] hover:bg-[#C99F53] text-black font-medium disabled:opacity-60"
          >
            Kirim
          </button>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <button
            @click="quickSend('mulai profiling')"
            class="text-xs px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200"
          >
            Mulai Profiling
          </button>
          <button
            @click="quickSend('apa itu undertone?')"
            class="text-xs px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200"
          >
            Edukasi Undertone
          </button>
          <button
            @click="quickSend('apa itu seasonal color?')"
            class="text-xs px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200"
          >
            Edukasi Seasonal
          </button>
        </div>

        <div class="mt-6 border-t border-gray-200 dark:border-gray-700 pt-4 space-y-3">
          <p class="text-sm text-gray-600 dark:text-gray-300">
            Session: <span class="font-semibold">{{ sessionId || '-' }}</span>
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-300">
            Hasil Profiling: <span class="font-semibold">{{ seasonalType ? `${seasonalType} (Y1=${y1Value})` : 'Belum lengkap' }}</span>
          </p>
          <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200">
            <input type="checkbox" v-model="disablePrice" />
            Nonaktifkan preferensi harga (renormalisasi bobot SAW)
          </label>
          <button
            @click="generateRecommendation"
            :disabled="!sessionId || !seasonalType || loadingRecommendation"
            class="w-full px-4 py-3 rounded-xl bg-gray-900 dark:bg-gray-100 dark:text-black text-white disabled:opacity-60"
          >
            {{ loadingRecommendation ? 'Memproses...' : 'Generate Rekomendasi' }}
          </button>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Ranking Produk</h2>
        <p class="text-sm text-gray-500 dark:text-gray-300 mt-2">
          Skor dihitung dari FIS Layer 2 + ROC + SAW.
        </p>

        <div v-if="weights" class="mt-4 text-xs text-gray-600 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 p-3 rounded-lg">
          Bobot aktif: C1={{ weights.c1 }}
          <span v-if="weights.c2 !== undefined"> | C2={{ weights.c2 }}</span>
          | C3={{ weights.c3 }} | C4={{ weights.c4 }}
        </div>

        <div class="mt-5 space-y-4 max-h-[640px] overflow-y-auto pr-1">
          <div
            v-for="item in recommendations"
            :key="item.product_id"
            class="border border-gray-200 dark:border-gray-700 rounded-xl p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm text-gray-500 dark:text-gray-400">Rank #{{ item.rank }}</p>
                <h3 class="font-semibold text-gray-900 dark:text-white">{{ item.product_name }}</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  SAW={{ item.saw_score }} · C1={{ item.skor_produk }}
                </p>
              </div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-200">Rp{{ formatNumber(item.price) }}</p>
            </div>

            <div class="mt-3 text-xs text-gray-600 dark:text-gray-300">
              Rating {{ item.rating }} · Terjual {{ item.sold_count }}
            </div>

            <div class="mt-3 flex flex-wrap gap-2">
              <div
                v-for="(c, idx) in item.color_details"
                :key="`${item.product_id}-${idx}`"
                class="text-xs px-2 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
              >
                {{ c.hex_code }} (Y2={{ c.y2 }})
              </div>
            </div>
          </div>

          <p v-if="recommendations.length === 0" class="text-sm text-gray-500 dark:text-gray-300">
            Belum ada data rekomendasi. Lengkapi profiling lalu klik Generate Rekomendasi.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { getRecommendations, sendChat } from '../services/seeraApi'

const messages = ref([
  { role: 'bot', text: 'Halo! Saya Seera Assistant. Ketik "mulai profiling" untuk mulai.' }
])
const inputMessage = ref('')
const sending = ref(false)
const loadingRecommendation = ref(false)

const sessionId = ref('')
const seasonalType = ref('')
const y1Value = ref(null)
const disablePrice = ref(false)
const recommendations = ref([])
const weights = ref(null)

const formatNumber = (value) => new Intl.NumberFormat('id-ID').format(value)

const pushUserMessage = (text) => {
  messages.value.push({ role: 'user', text })
}

const pushBotMessage = (text) => {
  messages.value.push({ role: 'bot', text })
}

const handleSend = async () => {
  const text = inputMessage.value.trim()
  if (!text || sending.value) return

  pushUserMessage(text)
  inputMessage.value = ''
  sending.value = true

  try {
    const response = await sendChat({
      session_id: sessionId.value || null,
      message: text
    })

    sessionId.value = response.session_id
    seasonalType.value = response.seasonal_type || ''
    y1Value.value = response.y1_value
    pushBotMessage(response.bot_message)
  } catch (error) {
    pushBotMessage(`Error: ${error.message}`)
  } finally {
    sending.value = false
  }
}

const quickSend = async (text) => {
  inputMessage.value = text
  await handleSend()
}

const generateRecommendation = async () => {
  if (!sessionId.value || !seasonalType.value) {
    pushBotMessage('Profiling belum lengkap. Lengkapi skin tone dan undertone terlebih dahulu.')
    return
  }

  loadingRecommendation.value = true
  try {
    const result = await getRecommendations({
      session_id: sessionId.value,
      disable_price: disablePrice.value
    })

    recommendations.value = result.recommendations
    weights.value = result.weights
    seasonalType.value = result.seasonal_type
    y1Value.value = result.y1_value
    pushBotMessage(`Rekomendasi berhasil dibuat untuk tipe ${result.seasonal_type}.`) 
  } catch (error) {
    pushBotMessage(`Gagal generate rekomendasi: ${error.message}`)
  } finally {
    loadingRecommendation.value = false
  }
}
</script>
