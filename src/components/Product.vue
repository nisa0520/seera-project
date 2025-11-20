<template>
  <div class="pt-0 dark:bg-black dark:text-white transition-colors duration-300">

    <!-- HERO -->
    <section class="relative w-full h-[200px] sm:h-[280px] md:h-[320px] overflow-hidden">
      <img 
        src="/product.png" 
        alt="Our Products" 
        class="w-full h-full object-cover object-center"
      >
      <div class="absolute inset-0 flex items-center justify-center">
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-serif text-black dark:text-white">
          Our Product
        </h1>
      </div>
    </section>

    <!-- MAIN WRAPPER -->
    <div class="w-full max-w-screen-2xl mx-auto px-6 sm:px-8 pt-10">

      <!-- FILTER TEXT + COUNT -->
      <div class="flex justify-between items-center mb-5">
        <button 
          @click="showFilter = !showFilter"
          class="flex items-center gap-2 text-lg cursor-pointer dark:text-white"
        >
          <img src="/filter.png" alt="filter" class="w-5 h-5 dark:invert">
          <span>Filter</span>
        </button>

        <p class="text-gray-700 dark:text-gray-300">
          {{ filteredProducts.length }} products
        </p>
      </div>

      <!-- FILTER PANEL -->
      <div
        v-if="showFilter"
        class="border p-6 rounded-lg mb-8 shadow-sm bg-white 
               dark:bg-gray-900 dark:border-gray-700 animate-fade"
      >
        <h3 class="font-semibold mb-3 dark:text-white">Price Range</h3>

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

        <h3 class="font-semibold mt-6 mb-3 dark:text-white">Availability</h3>

        <div class="flex flex-col gap-2 text-gray-700 dark:text-gray-300">
          <label class="flex items-center gap-2">
            <input type="checkbox" value="in" v-model="availability">
            In Stock Only
          </label>
          <label class="flex items-center gap-2">
            <input type="checkbox" value="out" v-model="availability">
            Out of Stock
          </label>
        </div>

        <div class="flex gap-3 mt-6">
          <button 
            @click="applyFilter"
            class="px-5 py-2 bg-black text-white rounded hover:bg-gray-800 
                   dark:bg-white dark:text-black dark:hover:bg-gray-200"
          >
            Apply
          </button>

          <button 
            @click="resetFilter"
            class="px-5 py-2 border rounded hover:bg-gray-100
                   dark:border-gray-600 dark:hover:bg-gray-800 dark:text-white"
          >
            Reset
          </button>
        </div>
      </div>

      <!-- PRODUCTS GRID -->
      <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 pb-24">

        <div 
          v-for="product in filteredProducts" 
          :key="product.id"
          class="bg-white dark:bg-gray-900 rounded-lg overflow-hidden shadow-sm 
                 hover:shadow-md transition-shadow cursor-pointer 
                 dark:border dark:border-gray-700"
        >
          <div class="relative">
            <img 
              :src="product.image" 
              :alt="product.name" 
              class="w-full h-64 sm:h-72 md:h-80 lg:h-96 object-cover"
            >

            <span 
              v-if="product.discount" 
              class="absolute top-2 left-2 bg-red-600 text-white text-xs px-3 py-1 font-semibold"
            >
              {{ product.discount }}
            </span>

            <button 
              class="absolute bottom-2 right-2 bg-white dark:bg-gray-800 rounded-full p-2 
                     shadow-md hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
            >
              <svg 
                class="w-5 h-5 text-gray-700 dark:text-gray-200" 
                fill="none" stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2"
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 
                     0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 
                     0 00-6.364 0z" 
                />
              </svg>
            </button>
          </div>

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
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const showFilter = ref(false);
const price = ref(1000000);
const availability = ref([]);

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
]);

const filteredProducts = computed(() => {
  return products.value.filter((p) => {
    const numericPrice = Number(p.price.replace(/[^\d]/g, ""));
    const priceMatch = numericPrice <= price.value;

    const isInStock = p.id % 2 === 0;

    const availabilityMatch =
      availability.value.length === 0 ||
      (availability.value.includes("in") && isInStock) ||
      (availability.value.includes("out") && !isInStock);

    return priceMatch && availabilityMatch;
  });
});

const applyFilter = () => (showFilter.value = false);

const resetFilter = () => {
  price.value = 1000000;
  availability.value = [];
};
</script>

<style>
/* Fade animation */
.animate-fade {
  animation: fadeIn 0.25s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
