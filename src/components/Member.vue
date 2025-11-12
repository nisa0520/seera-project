<template>
  <div class="pt-0">

    <!-- Page Title -->
    <section class="py-24 text-center">
      <h1 class="text-4xl font-serif">Membership</h1>
    </section>

    <!-- Hero Section -->
    <section class="relative w-full h-[380px] overflow-hidden">
      <img 
        src="/member.png"
        alt="Membership"
        class="w-full h-full object-cover"
      >

      <!-- Card -->
      <div 
        class="absolute inset-0 flex items-center px-6 lg:px-20" 
      >
        <div class="bg-[#725622] text-white max-w-md px-24 py-8 rounded-md shadow-lg text-center">
          <h2 class="text-2xl font-serif mb-2">Join Our Membership</h2>

          <p class="mb-6">
            Lorem ipsum dolor sit amet
          </p>

          <button 
            class="bg-[#C99F53] text-black px-6 py-2 rounded hover:bg-gray-200 transition"
          >
            Sign in
          </button>

          <p class="mt-4">
            Already have account?
            <a href="#" class="underline ml-1">Login</a>
          </p>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="px-6 py-20 max-w-4xl mx-auto">
      <h2 class="text-center text-2xl font-serif mb-12">Frequently Asked Question</h2>

      <div class="space-y-6">

        <div 
          v-for="(item, index) in faq"
          :key="index"
          class="border-b pb-4"
        >
          <!-- Question -->
          <div 
            class="flex justify-between items-center cursor-pointer select-none"
            @click="toggle(index)"
          >
            <p class="text-gray-800">{{ item.question }}</p>

            <span 
              class="text-xl transform transition-transform duration-300"
              :class="openIndex === index ? 'rotate-90' : ''"
            >
              ›
            </span>
          </div>

          <!-- Answer -->
          <transition name="fade">
            <p 
              v-if="openIndex === index"
              class="mt-3 text-gray-600"
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
    question: "Lorem ipsum dolor sit amet?",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua."
  },
  {
    question: "Lorem ipsum dolor sit amet?",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua."
  },
  {
    question: "Lorem ipsum dolor sit amet?",
    answer:
      "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua."
  }
]

function toggle(index) {
  openIndex.value = openIndex.value === index ? null : index
}
</script>

<style>
/* Fade animation for answer */
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
