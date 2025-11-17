<template>
  <div class="pt-32 pb-20 px-4 sm:px-6 flex flex-col items-center">
    <div class="w-full max-w-[280px] sm:max-w-[320px] md:max-w-[360px]">
      <!-- Title -->
      <h1 class="text-3xl font-semibold mb-10 text-center">Create Account</h1>

      <!-- Google Button -->
      <button 
        class="w-full bg-blue-50 border border-blue-200 py-3 rounded-md flex items-center justify-center gap-3 hover:bg-blue-100 transition"
      >
        <img src="https://www.svgrepo.com/show/475656/google-color.svg" class="w-5 h-5" />
        <span>Sign up with Google</span>
      </button>

      <!-- Divider -->
      <div class="flex items-center gap-5 w-full my-6">
        <div class="flex-1 border-t"></div>
        <span class="text-gray-500 text-sm">Or use Email</span>
        <div class="flex-1 border-t"></div>
      </div>

      <!-- FORM SIGN UP -->
      <div class="w-full space-y-4">

        <!-- First Name -->
        <div>
          <label class="text-xs uppercase text-gray-600">First Name</label>
          <input 
            type="text"
            placeholder="John"
            class="w-full border rounded-md py-3 px-4 bg-gray-50"
          />
        </div>

        <!-- Last Name -->
        <div>
          <label class="text-xs uppercase text-gray-600">Last Name</label>
          <input 
            type="text"
            placeholder="Doe"
            class="w-full border rounded-md py-3 px-4 bg-gray-50"
          />
        </div>

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
              placeholder="•••••••••••••••"
              class="w-full border rounded-md py-3 px-4 bg-gray-50"
            />
            <button 
              class="absolute right-4 top-3 text-gray-400"
              @click="showPassword = !showPassword"
            >
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>

              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Button Sign Up -->
        <button 
          class="w-full bg-yellow-700 text-white py-3 rounded-md hover:bg-yellow-800 transition"
        >
          SIGN UP
        </button>

      </div>

      <!-- Login Redirect -->
      <p class="mt-6 text-gray-700 text-sm text-center">
        Already have account?
        <RouterLink to="/login" class="font-semibold underline">LOG IN</RouterLink>
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