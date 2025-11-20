<template>
  <div class="pt-0 dark:bg-black dark:text-white">

    <!-- Page Title -->
    <section class="py-16 sm:py-20 md:py-24 text-center">
      <h1 class="text-3xl sm:text-4xl font-serif text-black dark:text-white">
        Membership
      </h1>
    </section>

    <!-- Hero Section -->
    <section 
      class="relative w-full h-[280px] sm:h-[320px] md:h-[380px] overflow-hidden mb-12 sm:mb-16 md:mb-20"
    >
      <img 
        src="/member.png"
        alt="Membership"
        class="w-full h-full object-cover"
      >

      <!-- Card -->
      <div 
        class="absolute inset-0 flex items-center justify-center md:justify-start px-4 sm:px-6 md:px-8 lg:px-20" 
      >
        <div 
          class="bg-[#725622] text-white w-full max-w-[280px] sm:max-w-xs md:max-w-sm lg:max-w-md 
                 px-6 sm:px-10 md:px-16 lg:px-24 py-6 sm:py-7 md:py-8 rounded-md shadow-lg text-center"
        >
          <h2 class="text-lg sm:text-xl md:text-2xl font-serif mb-2">
            Join Our Membership
          </h2>

          <p class="mb-4 sm:mb-5 md:mb-6 text-sm sm:text-base text-white">
            Lorem ipsum dolor sit amet
          </p>

          <button 
            class="bg-[#C99F53] text-black px-5 sm:px-6 py-2 rounded 
                   hover:bg-[#D4AF69] transition text-sm sm:text-base w-full sm:w-auto"
          >
            Sign in
          </button>

          <p class="mt-3 sm:mt-4 text-xs sm:text-sm text-white">
            Already have account?
            <a href="#" class="underline ml-1 text-white">Login</a>
          </p>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="px-4 sm:px-6 py-12 sm:py-16 md:py-20 max-w-4xl mx-auto">
      <h2 class="text-center text-xl sm:text-2xl font-serif mb-8 sm:mb-10 md:mb-12 
                 text-black dark:text-white">
        Frequently Asked Question
      </h2>

      <div class="space-y-4 sm:space-y-5 md:space-y-6">

        <div 
          v-for="(item, index) in faq"
          :key="index"
          class="border-b border-gray-200 dark:border-gray-700 pb-3 sm:pb-4"
        >
          <!-- Question -->
          <div 
            class="flex justify-between items-start cursor-pointer select-none gap-3 sm:gap-4"
            @click="toggle(index)"
          >
            <p 
              class="text-gray-800 dark:text-gray-300 text-sm sm:text-base flex-1 pr-2"
            >
              {{ item.question }}
            </p>

            <span 
              class="text-lg sm:text-xl transform transition-transform duration-300 
                     flex-shrink-0 mt-0.5 text-black dark:text-white"
              :class="openIndex === index ? 'rotate-90' : ''"
            >
              ›
            </span>
          </div>

          <!-- Answer -->
          <transition name="fade">
            <p 
              v-if="openIndex === index"
              class="mt-2 sm:mt-3 text-gray-600 dark:text-gray-400 
                     text-xs sm:text-sm md:text-base leading-relaxed"
            >
              {{ item.answer }}
            </p>
          </transition>
        </div>

      </div>
    </section>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const openIndex = ref(null)

const faq = [
  {
    question: "Kenapa harus jadi member?",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua."
  },
  {
    question: "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua."
  },
  {
    question: "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua."
  },
  {
    question: "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua."
  }
]

function toggle(index) {
  openIndex.value = openIndex.value === index ? null : index
}
</script>

<style>
/* Fade animation */
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  max-height: 0;
}
.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  max-height: 200px;
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}
</style>
