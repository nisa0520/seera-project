<template>
  <!-- Sidebar Overlay -->
  <div 
    v-if="isSidebarOpen" 
    @click="isSidebarOpen = false"
    class="fixed inset-0 bg-black bg-opacity-50 z-[60] transition-opacity duration-300"
  ></div>

  <!-- Sidebar Menu -->
  <div 
    :class="[
      'fixed top-0 left-0 h-full w-64 shadow-2xl z-[70] transform transition-all duration-300 ease-in-out',
      'bg-white dark:bg-gray-900',
      isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
    ]"
  >
    <div class="p-6">
      <!-- Close Button (Kiri Atas) -->
      <button 
        @click="isSidebarOpen = false"
        class="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white mb-8 transition-colors"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Menu Items (Center) -->
      <nav class="space-y-6 text-center">
        <RouterLink 
          to="/" 
          @click="isSidebarOpen = false"
          class="block text-gray-800 dark:text-white hover:text-[#C99F53] dark:hover:text-[#C99F53] text-lg font-medium transition-colors"
        >
          Home
        </RouterLink>
        <RouterLink 
          to="/about" 
          @click="isSidebarOpen = false"
          class="block text-gray-800 dark:text-white hover:text-[#C99F53] dark:hover:text-[#C99F53] text-lg font-medium transition-colors"
        >
          About
        </RouterLink>
        <RouterLink 
          to="/product" 
          @click="isSidebarOpen = false"
          class="block text-gray-800 dark:text-white hover:text-[#C99F53] dark:hover:text-[#C99F53] text-lg font-medium transition-colors"
        >
          Our Product
        </RouterLink>
        <RouterLink 
          to="/koleksi" 
          @click="isSidebarOpen = false"
          class="block text-gray-800 dark:text-white hover:text-[#C99F53] dark:hover:text-[#C99F53] text-lg font-medium transition-colors"
        >
          Collections
        </RouterLink>
        <RouterLink 
          to="/member" 
          @click="isSidebarOpen = false"
          class="block text-gray-800 dark:text-white hover:text-[#C99F53] dark:hover:text-[#C99F53] text-lg font-medium transition-colors"
        >
          Membership
        </RouterLink>
      </nav>
    </div>
  </div>

  <!-- CART SIDEBAR -->
  <div 
    v-if="isCartOpen" 
    @click="isCartOpen = false"
    class="fixed inset-0 bg-black bg-opacity-40 z-[60]"
  ></div>

  <div 
    :class="[
      'fixed top-0 right-0 h-full w-[380px] shadow-2xl z-[70] transform transition-all duration-300',
      'bg-white dark:bg-gray-900',
      isCartOpen ? 'translate-x-0' : 'translate-x-full'
    ]"
  >
    <div class="p-6 h-full flex flex-col">

      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Cart <span class="text-sm text-gray-500 dark:text-gray-400">(1)</span>
        </h2>

        <button @click="isCartOpen = false" class="text-gray-700 dark:text-gray-300 hover:text-black dark:hover:text-white transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Cart Item -->
      <div class="flex gap-4 mb-6 border-b dark:border-gray-700 pb-4">
        <img 
          src="/koko-hijau.png" 
          class="w-20 h-20 object-cover rounded-md"
        >

        <div class="flex flex-col flex-1">
          <p class="font-semibold text-gray-900 dark:text-white">Koko Pria</p>
          <p class="text-sm text-gray-500 dark:text-gray-400">Rp200.000</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">Hijau</p>

          <div class="flex items-center gap-3 mt-2">
            <button class="px-2 py-1 bg-gray-200 dark:bg-gray-700 dark:text-white transition-colors">-</button>
            <span class="dark:text-white">1</span>
            <button class="px-2 py-1 bg-gray-200 dark:bg-gray-700 dark:text-white transition-colors">+</button>

            <button class="ml-auto text-gray-500 dark:text-gray-400 hover:text-black dark:hover:text-white transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Coupon -->
      <div>
        <p class="text-sm text-gray-700 dark:text-gray-300 mb-2">Enter discount code here</p>
        <div class="flex border dark:border-gray-700">
          <input 
            type="text" 
            class="flex-1 px-3 py-2 border-r dark:border-gray-700 outline-none bg-white dark:bg-gray-800 dark:text-white transition-colors"
            placeholder="Discount code"
          >
          <button class="px-4 bg-[#b48b3c] text-black hover:bg-[#C99F53] transition-colors">Apply</button>
        </div>
      </div>

      <!-- Total -->
      <div class="mt-6 border-t dark:border-gray-700 pt-4 flex justify-between font-semibold text-gray-800 dark:text-white">
        <span>Total</span>
        <span>Rp200.000</span>
      </div>

      <!-- Checkout Button -->
      <button @click="goCheckout"
        class="mt-4 w-full py-3 bg-[#b48b3c] text-black font-semibold hover:bg-[#C99F53] transition-colors"
      >
        Checkout
      </button>

    </div>
  </div>

  <!-- Navbar -->
  <nav 
    :class="[
      'py-6 px-8 flex items-center justify-between fixed top-0 left-0 right-0 z-50 transition-all duration-300',
      isScrolled ? 'bg-gray-200 dark:bg-gray-900 shadow-md' : 'bg-transparent'
    ]"
  >
    <div class="flex items-center gap-6">
      <!-- Hamburger Menu Button -->
      <button 
        @click="isSidebarOpen = true"
        :class="isScrolled ? 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white' : 'text-black dark:text-white hover:text-gray-200'"
        class="transition-colors"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      
      <!-- Search Button -->
      <button 
        :class="isScrolled ? 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white' : 'text-black dark:text-white hover:text-gray-200'"
        class="transition-colors"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </button>
    </div>
    
    <!-- Logo -->
    <div class="flex items-center gap-3">
      <RouterLink to="/">
        <img src="/logo.svg" alt="Seera Project" class="h-10">
      </RouterLink>
    </div>
    
    <!-- Right Side Icons -->
    <div class="flex items-center gap-6">
      <!-- User Icon -->
      <RouterLink to="/login">
        <button 
          :class="isScrolled ? 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white' : 'text-black dark:text-white hover:text-gray-200'"
          class="transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </button>
      </RouterLink>
      
      <!-- Cart Icon -->
      <button 
        @click="isCartOpen = true"
        :class="isScrolled ? 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white' : 'text-black dark:text-white hover:text-gray-200'"
        class="transition-colors"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </button>
      
      <!-- Dark/Light Mode Toggle -->
      <button 
        @click="toggleDarkMode" 
        :class="[
          'rounded-full p-2 transition-all',
          isScrolled ? 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white' : 'bg-white bg-opacity-20 dark:bg-gray-800 dark:bg-opacity-50 text-black dark:text-white hover:bg-opacity-30 dark:hover:bg-opacity-70'
        ]"
      >
        <!-- Sun Icon (Light Mode) -->
        <svg v-if="isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        
        <!-- Moon Icon (Dark Mode) -->
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isScrolled = ref(false)
const isDark = ref(false)
const isSidebarOpen = ref(false)
const isCartOpen = ref(false)

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

const goCheckout = () => {
  router.push('/checkout')
}

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('darkMode', 'true')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('darkMode', 'false')
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  const savedDarkMode = localStorage.getItem('darkMode')
  if (savedDarkMode === 'true') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>