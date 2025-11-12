<template>
  <div class="pt-32 pb-20 flex flex-col items-center">

    <!-- Title -->
    <h1 class="text-3xl font-semibold mb-10">Login</h1>

    <!-- Google Button -->
    <button 
      class="w-[360px] bg-blue-50 border border-blue-200 py-3 rounded-md flex items-center justify-center gap-3 hover:bg-blue-100 transition"
    >
      <img src="https://www.svgrepo.com/show/475656/google-color.svg" class="w-5 h-5" />
      <span>Sign up with Google</span>
    </button>

    <!-- Divider -->
    <div class="flex items-center gap-5 w-[360px] my-6">
      <div class="flex-1 border-t"></div>
      <span class="text-gray-500 text-sm">Or use Email</span>
      <div class="flex-1 border-t"></div>
    </div>

    <!-- FORM LOGIN -->
    <div class="w-[360px] space-y-4">

      <!-- Email -->
      <div>
        <label class="text-xs uppercase text-gray-600">Email</label>
        <input 
          type="email"
          placeholder="johndoe@email.com"
          class="w-full border rounded-md py-3 px-4 bg-gray-50"
        />
      </div>

      <!-- Password -->
      <div>
        <label class="text-xs uppercase text-gray-600">Password</label>
        <div class="relative">
          <input 
            :type="showPassword ? 'text' : 'password'"
            placeholder="•••••••••••"
            class="w-full border rounded-md py-3 px-4 bg-gray-50"
          />
          <button 
            class="absolute right-4 top-3 text-gray-500"
            @click="showPassword = !showPassword"
          >
            <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.03-10-7s4.477-7 10-7c2.044 0 3.93.612 5.5 1.625M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>

            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3l18 18M10.477 10.477A3 3 0 0113.5 13.5m3.086 3.086C15.93 17.388 14.036 18 12 18c-5.523 0-10-4.03-10-7 0-2.042 1.119-3.888 2.843-5.171m5.13-2.606A9.956 9.956 0 0112 5c5.523 0 10 4.03 10 7a6.959 6.959 0 01-.663 2.75" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Button Login -->
      <button 
        class="w-full bg-yellow-700 text-white py-3 rounded-md hover:bg-yellow-800 transition"
      >
        LOGIN
      </button>

    </div>

    <!-- Sign Up Redirect -->
    <p class="mt-6 text-gray-700 text-sm">
      Don't have account?
      <RouterLink to="/signup" class="font-semibold underline">SIGN UP</RouterLink>
    </p>

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
