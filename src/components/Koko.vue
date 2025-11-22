<template>
  <section class="pt-0 pb-20 bg-gray-50 dark:bg-black transition-colors duration-300">

    <!-- HERO -->
    <div class="relative w-full h-[260px] sm:h-[300px] md:h-[340px] overflow-hidden">
      <div class="absolute inset-0 flex items-center justify-center">
        <h1 class="text-4xl sm:text-5xl font-serif font-semibold text-black dark:text-white">
          Koko
        </h1>
      </div>
    </div>

    <!-- MAIN WRAPPER -->
    <div class="w-full max-w-screen-2xl mx-auto px-6 sm:px-8">

      <!-- FILTER HEADER -->
      <div class="flex justify-between items-center mb-6">
        <button 
          @click="showFilter = !showFilter"
          class="flex items-center gap-2 text-lg cursor-pointer text-gray-900 dark:text-white"
        >
          <img 
            src="/filter.png" 
            alt="filter" 
            class="w-5 h-5 invert dark:invert-0"
          >
          <span>Filter</span>
        </button>

        <p class="text-gray-700 dark:text-gray-300">
          {{ filteredProducts.length }} products
        </p>
      </div>

      <!-- FILTER PANEL -->
      <transition name="fade">
        <div 
          v-if="showFilter"
          class="border border-gray-300 dark:border-gray-700 
                 p-6 rounded-lg mb-10 shadow-sm 
                 bg-white dark:bg-gray-900 
                 text-gray-900 dark:text-gray-200"
        >
          <h3 class="font-semibold mb-3">Price Range</h3>

          <div class="flex items-center gap-3">
            <input 
              type="range"
              min="0"
              max="1000000"
              step="50000"
              v-model="price"
              class="w-full"
            />
            <span class="text-gray-700 dark:text-gray-300">
              Rp{{ price.toLocaleString() }}
            </span>
          </div>

          <!-- Availability -->
          <h3 class="font-semibold mt-6 mb-3">Availability</h3>

          <div class="flex flex-col gap-2 text-gray-700 dark:text-gray-300">
            <label class="flex items-center gap-2">
              <input type="checkbox" value="in" v-model="availability"> In Stock Only
            </label>
            <label class="flex items-center gap-2">
              <input type="checkbox" value="out" v-model="availability"> Out of Stock
            </label>
          </div>

          <!-- Buttons -->
          <div class="flex gap-3 mt-6">
            <button 
              @click="applyFilter"
              class="px-5 py-2 bg-black text-white rounded hover:bg-gray-800 
                     dark:bg-gray-800 dark:hover:bg-gray-700 transition-all"
            >
              Apply
            </button>

            <button 
              @click="resetFilter"
              class="px-5 py-2 border border-gray-300 dark:border-gray-600 
                     rounded hover:bg-gray-100 dark:hover:bg-gray-800 
                     text-gray-900 dark:text-gray-200 transition-all"
            >
              Reset
            </button>
          </div>
        </div>
      </transition>

      <!-- PRODUCTS GRID -->
      <div
        class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 
               gap-6 mb-8"
      >
        <div 
          v-for="product in filteredProducts"
          :key="product.id"
          @click="$router.push(`/productdetail/${product.id}`)"
          class="bg-white dark:bg-gray-900 rounded-lg overflow-hidden 
                 shadow-sm hover:shadow-md dark:hover:shadow-lg 
                 transition-shadow cursor-pointer"
        >
          <!-- Image -->
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
              class="absolute bottom-2 right-2 bg-white dark:bg-gray-800 
                     rounded-full p-2 shadow-md 
                     hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >
              <svg 
                class="w-5 h-5 text-gray-700 dark:text-gray-300" 
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

          <!-- Info -->
          <div class="p-4 text-center sm:text-left">
            <h3 class="text-gray-900 dark:text-white font-semibold mb-1 text-sm sm:text-base md:text-lg">
              {{ product.name }}
            </h3>
            <p class="text-gray-700 dark:text-gray-300 text-sm sm:text-base">
              {{ product.price }}
            </p>
          </div>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'

const showFilter = ref(false)
const price = ref(1000000)
const availability = ref([])

const products = ref([
  { id: 1, name: 'Koko Pria Premium', price: 'Rp250.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400' },
  { id: 2, name: 'Gamis Wanita Elegant', price: 'Rp280.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { id: 3, name: 'Koko Pria Modern', price: 'Rp290.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400' },
  { id: 4, name: 'Koko Pria Classic', price: 'Rp200.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400' },
  { id: 5, name: 'Koko Pria Casual', price: 'Rp220.000', image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400' },
  { id: 6, name: 'Gamis Wanita Syari', price: 'Rp300.000', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { id: 7, name: 'Koko Pria Executive', price: 'Rp350.000', image: 'https://images.unsplash.com/photo-1578632292335-df3abbb0d586?w=400' },
  { id: 8, name: 'Koko Pria Trendy', price: 'Rp240.000', image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400' },
  { id: 9, name: 'Gamis Wanita Premium', price: 'Rp320.000', discount: 'Best Seller', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { id: 10, name: 'Koko Pria Formal', price: 'Rp275.000', image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400' },
  { id: 11, name: 'Gamis Wanita Daily', price: 'Rp260.000', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { id: 12, name: 'Koko Pria Simpel', price: 'Rp210.000', discount: 'Sale', image: 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400' },
])

const filteredProducts = computed(() => {
  return products.value.filter(p => {
    const numericPrice = Number(p.price.replace(/[^\d]/g, ""))
    const priceMatch = numericPrice <= price.value

    const isInStock = p.id % 2 === 0 // contoh dummy
    const availabilityMatch =
      availability.value.length === 0 ||
      (availability.value.includes("in") && isInStock) ||
      (availability.value.includes("out") && !isInStock)

    return priceMatch && availabilityMatch
  })
})

const applyFilter = () => {
  showFilter.value = false
}

const resetFilter = () => {
  price.value = 1000000
  availability.value = []
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity .3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
