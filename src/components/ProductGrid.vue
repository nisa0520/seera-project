<template>
  <section class="py-16 bg-gray-50">
    <div class="w-full max-w-screen-2xl mx-auto px-6 sm:px-8">
      <h2 class="font-serif text-4xl font-semibold text-center mb-12 text-gray-900">
        {{ title }}
      </h2>

      <!-- Responsive Product Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-8">
        <div
          v-for="product in products"
          :key="product.id"
          class="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
        >
          <!-- Product Image -->
          <div class="relative">
            <img
              :src="product.image"
              :alt="product.name"
              class="w-full h-64 sm:h-72 md:h-80 lg:h-96 object-cover"
            />
            <span
              v-if="product.discount"
              class="absolute top-2 left-2 bg-red-600 text-white text-xs px-3 py-1 font-semibold"
            >
              {{ product.discount }}
            </span>
            <button
              class="absolute bottom-2 right-2 bg-white rounded-full p-2 shadow-md hover:bg-gray-100"
            >
              <svg
                class="w-5 h-5 text-gray-700"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
            </button>
          </div>

          <!-- Product Info -->
          <div class="p-4 text-center sm:text-left">
            <h3 class="text-gray-900 font-semibold mb-1 text-sm sm:text-base md:text-lg">
              {{ product.name }}
            </h3>
            <p class="text-gray-700 text-sm sm:text-base">
              {{ product.price }}
            </p>
          </div>
        </div>
      </div>

      <!-- Button -->
      <div class="text-center">
        <button
          class="bg-seera-gold text-black px-10 sm:px-12 py-3 font-semibold hover:bg-opacity-90 transition-all"
        >
          View All
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: String,
  products: Array
})
</script>
