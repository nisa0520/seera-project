<template>
  <section class="py-16 bg-white">
    <div class="w-full max-w-screen-2xl mx-auto px-8">
    <h2 class="font-serif text-4xl font-semibold text-center mb-12 text-gray-900">Testimonial</h2>
    
    <div class="grid grid-cols-3 gap-8">
      <div v-for="testimonial in testimonials" :key="testimonial.name" class="bg-gray-50 p-6 rounded-lg">
        <p class="text-gray-700 mb-4 leading-relaxed text-lg">{{ testimonial.text }}</p>
        <p class="text-gray-700 mb-4 leading-relaxed text-lg">{{ testimonial.text2 }}</p>
        <div class="flex gap-1 mb-4">
          <svg v-for="i in testimonial.rating" :key="i" class="w-5 h-20 text-seera-gold" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        </div>
        <p class="font-semibold text-lg text-gray-900">{{ testimonial.name }}</p>
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
    text2: 'Ut enim ad minim veniam, quis nostrum exercitationem ullam corporis suscipit.'
  },
  {
    name: 'Fatima',
    rating: 5,
    text: 'Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.',
    text2: 'Quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequat.'
  },
  {
    name: 'Azizah',
    rating: 4,
    text: 'Lorem ipsum dolor sit amet, consectetur adipisci elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua.',
    text2: 'Ut enim ad minim veniam, quis nostrum exercitationem ullam corporis suscipit.'
  }
]
</script>