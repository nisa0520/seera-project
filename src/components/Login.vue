<template>
  <div class="pt-32 pb-20 px-4 sm:px-6 flex flex-col items-center dark:bg-black dark:text-white transition-colors duration-300">

    <div class="w-full max-w-[280px] sm:max-w-[320px] md:max-w-[360px]">

      <!-- Title -->
      <h1 class="text-3xl font-semibold mb-10 text-center text-gray-900 dark:text-white">
        Login
      </h1>

      <!-- Google Button -->
      <button 
        class="w-full bg-blue-50 dark:bg-gray-800 border border-blue-200 dark:border-gray-700 
               py-3 rounded-md flex items-center justify-center gap-3 
               hover:bg-blue-100 dark:hover:bg-gray-700 transition"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        <span class="text-gray-700 dark:text-gray-200">Sign up with Google</span>
      </button>

      <!-- Divider -->
      <div class="flex items-center gap-5 w-full my-6">
        <div class="flex-1 border-t dark:border-gray-700"></div>
        <span class="text-gray-500 dark:text-gray-400 text-sm">Or use Email</span>
        <div class="flex-1 border-t dark:border-gray-700"></div>
      </div>

      <!-- FORM LOGIN -->
      <div class="w-full space-y-4">

        <!-- Email -->
        <div>
          <label class="text-xs uppercase text-gray-600 dark:text-gray-300">Email</label>
          <input 
            type="email"
            placeholder="johndoe@email.com"
            class="w-full border dark:border-gray-700 rounded-md py-3 px-4 
                   bg-gray-50 dark:bg-gray-900 text-black dark:text-white"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="text-xs uppercase text-gray-600 dark:text-gray-300">Password</label>
          <div class="relative">
            <input 
              :type="showPassword ? 'text' : 'password'"
              placeholder="•••••••••••"
              class="w-full border dark:border-gray-700 rounded-md py-3 px-4 
                     bg-gray-50 dark:bg-gray-900 text-black dark:text-white"
            />

            <button 
              class="absolute right-4 top-3 text-gray-500 dark:text-gray-300"
              @click="showPassword = !showPassword"
            >
              <!-- visible -->
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.03-10-7s4.477-7 10-7c2.044 0 3.93.612 5.5 1.625M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>

              <!-- hidden -->
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M3 3l18 18M10.477 10.477A3 3 0 0113.5 13.5m3.086 3.086C15.93 17.388 14.036 18 12 18c-5.523 0-10-4.03-10-7 
                     0-2.042 1.119-3.888 2.843-5.171m5.13-2.606A9.956 9.956 0 0112 5c5.523 0 10 4.03 10 7a6.959 6.959 0 
                     01-.663 2.75" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Button Login -->
        <button 
          class="w-full bg-[#C99F53] text-black py-3 rounded-md 
                 hover:bg-[#b89049] dark:bg-[#C99F53] dark:text-black dark:hover:bg-[#b89049] 
                 transition"
        >
          LOGIN
        </button>

      </div>

      <!-- Sign Up Redirect -->
      <p class="mt-6 text-gray-700 dark:text-gray-300 text-sm text-center">
        Don't have account?
        <RouterLink to="/signup" class="font-semibold underline">SIGN UP</RouterLink>
      </p>
    </div>

    <!-- Footer Section -->
    <div class="w-full mt-20">
      <FooterComponent />
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
const showPassword = ref(false)
</script>
