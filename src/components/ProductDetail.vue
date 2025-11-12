<template>
  <div class="max-w-screen-xl mx-auto px-6 lg:px-10 py-32">

    <!-- WRAPPER -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">

      <!-- LEFT PRODUCT IMAGE -->
      <div>
        <img 
          :src="product.image"
          class="w-full aspect-square object-cover bg-gray-200"
        />

        <!-- thumbnail preview -->
        <div class="flex gap-3 mt-4">
          <img 
            v-for="n in 5" :key="n"
            :src="product.image"
            class="w-16 h-16 object-cover bg-gray-200 cursor-pointer hover:opacity-80"
          />
        </div>

        <p class="mt-6 text-sm">
          Warna : <span class="font-semibold">{{ product.color }}</span>
        </p>
      </div>

      <!-- RIGHT PRODUCT DETAILS -->
      <div>
        <!-- WISHLIST ICON -->
        <div class="flex justify-between items-start mb-4">
          <div>
            <h1 class="text-4xl font-normal mb-2">{{ product.name }}</h1>
            <p class="text-3xl text-yellow-700 font-normal">{{ product.price }}</p>
          </div>
          <button class="text-2xl">♡</button>
        </div>

        <!-- SIZE SELECTOR -->
        <div class="mt-8 flex gap-2">
          <button 
            v-for="size in sizes"
            :key="size"
            @click="selectedSize = size"
            :class="[
              'border border-gray-300 px-5 py-2 text-sm',
              selectedSize === size ? 'bg-yellow-700 text-white border-yellow-700' : 'bg-white'
            ]"
          >
            {{ size }}
          </button>
        </div>

        <!-- QTY -->
        <div class="mt-6 flex items-center gap-6">
          <button @click="qty > 1 && qty--" class="border border-gray-300 px-5 py-2 text-lg bg-white">−</button>
          <span class="text-lg min-w-[20px] text-center">{{ qty }}</span>
          <button @click="qty++" class="border border-gray-300 px-5 py-2 text-lg bg-white">+</button>
        </div>

        <!-- ADD TO CART BUTTON -->
        <button 
          class="w-full mt-6 bg-yellow-700 text-white py-3 text-base hover:bg-yellow-800 transition"
        >
          Add to Cart
        </button>

        <!-- DESCRIPTION -->
        <div class="mt-10">
          <h2 class="text-lg font-semibold mb-3">Description</h2>
          <p class="text-gray-700 text-sm leading-relaxed">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur. Quis aute iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
          </p>

          <button class="mt-3 text-sm text-gray-600 hover:text-black flex items-center gap-1">
            See more →
          </button>
        </div>

      </div>
    </div>

    <!-- REVIEW -->
    <div class="mt-16 w-full">
      <h2 class="text-2xl mb-6">Review</h2>

      <h3 class="font-semibold text-lg">Fatima</h3>

      <div class="flex text-yellow-500 mb-3 text-lg">
        <span v-for="n in 5" :key="n">★</span>
      </div>

      <p class="text-gray-700 text-sm leading-relaxed mb-6">
        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur.
      </p>

      <button class="bg-yellow-700 text-white px-8 py-3 hover:bg-yellow-800">
        Add Review
      </button>
    </div>

    <!-- YOU MAY ALSO LIKE -->
    <div class="mt-20">
      <h2 class="text-3xl mb-8">You May Also Like</h2>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        
        <div 
          v-for="item in recommended"
          :key="item.id"
          @click="$router.push(`/productdetail/${item.id}`)"
          class="bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        >
          <div class="relative">
            <img :src="item.image" class="w-full h-96 object-cover" />
            
            <button class="absolute bottom-2 right-2 bg-white rounded-full p-2 shadow-md hover:bg-gray-100">
              <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>
          </div>

          <div class="p-4">
            <h3 class="text-gray-900 font-semibold mb-1">{{ item.name }}</h3>
            <p class="text-gray-700">{{ item.price }}</p>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const product = ref({
  id: null,
  name: '',
  price: '',
  image: '',
  color: 'Maroon'
})

const sizes = ['S','M','L','XL','XXL']
const selectedSize = ref('M')
const qty = ref(1)

const recommended = ref([
  { id: 101, name: 'Koko Pria', price: 'Rp200.000', image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400'},
  { id: 102, name: 'Gamis Wanita', price: 'Rp200.000', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400'},
  { id: 103, name: 'Koko Pria', price: 'Rp200.000', image: 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400'},
  { id: 104, name: 'Koko Pria', price: 'Rp200.000', image: 'https://images.unsplash.com/photo-1578632292335-df3abbb0d586?w=400'},
])

// Simulate fetch product by ID
onMounted(() => {
  const id = Number(route.params.id)
  product.value = {
    id,
    name: 'Koko Pria',
    price: 'Rp200.000',
    image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400',
    color: 'Maroon'
  }
})
</script>