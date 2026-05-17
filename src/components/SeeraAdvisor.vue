<template>
  <section class="pt-32 pb-20 px-6 md:px-16 bg-gray-50 dark:bg-gray-900 min-h-screen">
    <div class="max-w-2xl mx-auto text-center">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-10">
        <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-[#C9A86A] to-[#8B6914] flex items-center justify-center">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>

        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-3">Seera Color Advisor</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-8 max-w-md mx-auto">
          Chatbot rekomendasi warna pakaian berdasarkan skin tone & undertone Anda menggunakan Fuzzy Logic, ROC, dan SAW.
        </p>

        <div class="grid sm:grid-cols-3 gap-4 mb-8 text-left">
          <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
            <div class="text-2xl mb-2">🎨</div>
            <h3 class="font-semibold text-gray-900 dark:text-white text-sm">Profiling Warna</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Analisis skin tone & undertone Anda</p>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
            <div class="text-2xl mb-2">📊</div>
            <h3 class="font-semibold text-gray-900 dark:text-white text-sm">Rekomendasi SAW</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Ranking produk dengan multi-kriteria</p>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-4">
            <div class="text-2xl mb-2">📚</div>
            <h3 class="font-semibold text-gray-900 dark:text-white text-sm">Edukasi Warna</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Pelajari seasonal color theory</p>
          </div>
        </div>

        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          Klik tombol chat melayang di pojok kanan bawah untuk memulai percakapan dengan Seera Assistant.
        </p>

        <div class="inline-flex items-center gap-2 text-[#C9A86A] text-sm font-medium">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          Lihat bubble chat di kanan bawah →
        </div>
      </div>
    </div>
  </section>
</template>
