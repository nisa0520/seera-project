<template>
  <section class="py-16 bg-white dark:bg-black transition-colors duration-300">
    <div class="w-full max-w-screen-2xl mx-auto px-6 sm:px-8">

      <h2 class="font-serif text-4xl font-semibold text-center mb-12 text-gray-900 dark:text-white transition-colors">
        Collections
      </h2>

      <RouterLink to="/koko">
        <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
          <div
            v-for="collection in collections"
            :key="collection.name"
            class="relative group cursor-pointer overflow-hidden rounded-lg"
          >
            <img
              :src="collection.image"
              :alt="collection.name"
              class="w-full h-64 sm:h-72 md:h-80 object-cover transition-transform duration-300 group-hover:scale-110"
            />

            <!-- Overlay (tetap gelap tapi lebih soft saat dark mode) -->
            <div
              class="absolute inset-0 bg-black/30 dark:bg-black/40 flex items-center justify-center transition-colors"
            >
              <h3 class="font-serif text-white text-xl sm:text-2xl font-semibold drop-shadow-lg">
                {{ collection.name }}
              </h3>
            </div>
          </div>
        </div>
      </RouterLink>

      <div class="text-center">
        <RouterLink to="/koleksi">
          <button
            class="bg-seera-gold dark:bg-[#C99F53] text-black dark:text-white px-10 sm:px-12 py-3 font-semibold rounded-md hover:bg-opacity-90 dark:hover:bg-[#D4AF69] transition-all"
          >
            View All
          </button>
        </RouterLink>
      </div>

    </div>
  </section>
</template>

<script setup>
const collections = [
  { name: 'Gamis', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { name: 'Koko', image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400' },
  { name: 'Abaya', image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400' },
  { name: 'Accessories', image: 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400' },
]
</script>
