<template>
  <section class="py-16 bg-white dark:bg-black transition-colors duration-300">
    <div class="w-full max-w-screen-2xl mx-auto px-4 sm:px-8">
      <h2 class="font-serif text-4xl font-semibold text-center mb-12 text-gray-900 dark:text-white">
        Testimonial
      </h2>

      <!-- Responsive scroll container -->
      <div
        class="flex overflow-x-auto gap-6 md:grid md:grid-cols-3 md:gap-8 scrollbar-hide snap-x snap-mandatory scroll-smooth"
      >
        <div
          v-for="testimonial in testimonials"
          :key="testimonial.name"
          class="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 flex-shrink-0 w-[90%] sm:w-[70%] md:w-auto snap-center shadow-sm hover:shadow-md dark:hover:shadow-lg transition-all duration-300"
        >
          <div class="flex flex-col">
            <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed text-base sm:text-lg">
              {{ testimonial.text }}
            </p>
            <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed text-base sm:text-lg">
              {{ testimonial.text2 }}
            </p>

            <div class="flex gap-1 mb-4">
              <svg
                v-for="i in testimonial.rating"
                :key="i"
                class="w-5 h-5 text-seera-gold"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                />
              </svg>
            </div>

            <p class="font-semibold text-lg text-gray-900 dark:text-white">
              {{ testimonial.name }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const testimonials = [
  {
    name: 'Siti',
    rating: 5,
    text: 'Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.',
    text2: 'Ut enim ad minim veniam, quis nostrum exercitationem ullam corporis suscipit.',
  },
  {
    name: 'Fatima',
    rating: 5,
    text: 'Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.',
    text2: 'Quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequat.',
  },
  {
    name: 'Azizah',
    rating: 4,
    text: 'Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.',
    text2: 'Ut enim ad minim veniam, quis nostrum exercitationem ullam corporis suscipit.',
  },
]
</script>

<style scoped>
/* Hide scrollbar for mobile */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
