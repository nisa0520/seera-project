<template>
  <div class="pt-0 min-h-screen bg-white dark:bg-black transition-colors duration-300"> 
    <!-- Hero Section -->
    <section class="relative w-full h-[200px] sm:h-[280px] md:h-[320px] overflow-hidden">
      <img 
        src="/contact.png" 
        alt="Contact Seera" 
        class="w-full h-full object-cover object-center"
      >
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center px-4">
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-serif text-black dark:text-white">Contact Us</h1>
        <p class="text-sm sm:text-lg md:text-xl font-serif text-gray-500 dark:text-gray-400 mt-2">Any question or remarks? Just write us a message!</p>
      </div>
    </section>

    <!-- Contact Form Section -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 py-12 sm:py-16 md:py-20">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
        
        <!-- Left Side - Contact Information -->
        <div class="bg-[#725622] dark:bg-[#5a4419] rounded-2xl sm:rounded-3xl p-6 sm:p-8 md:p-10 text-white relative overflow-hidden transition-colors duration-300">
          <h2 class="text-2xl sm:text-3xl font-serif mb-3 sm:mb-4">Contact Information</h2>
          <p class="text-amber-100 mb-8 sm:mb-12 text-sm sm:text-base">Say something to start a live chat!</p>

          <div class="space-y-6 sm:space-y-8 relative z-10">
            <!-- Phone -->
            <div class="flex items-center gap-3 sm:gap-4">
              <svg class="w-5 h-5 sm:w-6 sm:h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span class="text-sm sm:text-base">+1012 3456 789</span>
            </div>

            <!-- Email -->
            <div class="flex items-center gap-3 sm:gap-4">
              <svg class="w-5 h-5 sm:w-6 sm:h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span class="text-sm sm:text-base">demo@gmail.com</span>
            </div>

            <!-- Address -->
            <div class="flex items-start gap-3 sm:gap-4">
              <svg class="w-5 h-5 sm:w-6 sm:h-6 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span class="text-sm sm:text-base">132 Dartmouth Street Boston,<br>Massachusetts 02156 United States</span>
            </div>
          </div>

          <!-- Social Media Icons -->
          <div class="flex gap-3 sm:gap-4 mt-10 sm:mt-16 relative z-10">
            <a href="#" class="w-8 h-8 sm:w-10 sm:h-10 bg-[#C79D53] rounded-full flex items-center justify-center hover:bg-amber-600 transition-colors">
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z"/>
              </svg>
            </a>
            <a href="#" class="w-8 h-8 sm:w-10 sm:h-10 bg-[#C79D53] rounded-full flex items-center justify-center hover:bg-amber-600 transition-colors">
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
            </a>
            <a href="#" class="w-8 h-8 sm:w-10 sm:h-10 bg-[#C79D53] rounded-full flex items-center justify-center hover:bg-amber-600 transition-colors">
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"/>
              </svg>
            </a>
          </div>

          <!-- Decorative Circles -->
          <div class="absolute bottom-0 right-0 w-32 sm:w-48 h-32 sm:h-48 bg-[#C79D53] rounded-full opacity-20 translate-x-16 translate-y-16"></div>
          <div class="absolute bottom-16 sm:bottom-20 right-12 sm:right-20 w-20 sm:w-32 h-20 sm:h-32 bg-[#C99F53] rounded-full opacity-30"></div>
        </div>

        <!-- Right Side - Contact Form -->
        <div class="space-y-4 sm:space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <!-- First Name -->
            <div>
              <label class="block text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">First Name</label>
              <input 
                type="text" 
                v-model="form.firstName"
                placeholder="John"
                class="w-full border-b-2 border-gray-300 dark:border-gray-600 focus:border-[#C99F53] dark:focus:border-[#C99F53] outline-none py-2 text-sm sm:text-base bg-transparent text-black dark:text-white transition-colors"
              >
            </div>

            <!-- Last Name -->
            <div>
              <label class="block text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">Last Name</label>
              <input 
                type="text" 
                v-model="form.lastName"
                placeholder="Doe"
                class="w-full border-b-2 border-gray-300 dark:border-gray-600 focus:border-[#C99F53] dark:focus:border-[#C99F53] outline-none py-2 text-sm sm:text-base bg-transparent text-black dark:text-white transition-colors"
              >
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <!-- Email -->
            <div>
              <label class="block text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">Email</label>
              <input 
                type="email" 
                v-model="form.email"
                placeholder="johndoe@email.com"
                class="w-full border-b-2 border-gray-300 dark:border-gray-600 focus:border-[#C99F53] dark:focus:border-[#C99F53] outline-none py-2 text-sm sm:text-base bg-transparent text-black dark:text-white transition-colors"
              >
            </div>

            <!-- Phone Number -->
            <div>
              <label class="block text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">Phone Number</label>
              <input 
                type="tel" 
                v-model="form.phone"
                placeholder="+1 012 3456 789"
                class="w-full border-b-2 border-gray-300 dark:border-gray-600 focus:border-[#C99F53] dark:focus:border-[#C99F53] outline-none py-2 text-sm sm:text-base bg-transparent text-black dark:text-white transition-colors"
              >
            </div>
          </div>

          <!-- Message -->
          <div>
            <label class="block text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">Message</label>
            <textarea 
              v-model="form.message"
              placeholder="Write your message.."
              rows="4"
              class="w-full border-b-2 border-gray-300 dark:border-gray-600 focus:border-[#C99F53] dark:focus:border-[#C99F53] outline-none py-2 resize-none text-sm sm:text-base bg-transparent text-black dark:text-white transition-colors"
            ></textarea>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end pt-2 sm:pt-4">
            <button 
              @click="sendMessage"
              class="bg-[#C99F53] hover:bg-[#B48B3C] dark:hover:bg-[#D4AF69] text-black px-8 sm:px-12 py-2.5 sm:py-3 rounded-md transition-colors font-medium text-sm sm:text-base"
            >
              Send Message
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  message: ''
})

const sendMessage = () => {
  console.log('Sending message:', form.value)
  alert('Message sent successfully!')
  
  // Reset form
  form.value = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    message: ''
  }
}
</script>