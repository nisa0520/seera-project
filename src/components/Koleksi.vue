<template>
  <div class="pt-0"> 
    <!-- Hero Section -->
    <section class="relative w-full h-[320px] overflow-hidden">
      <img 
        src="/collect.png" 
        alt="About Seera" 
        class="w-full h-full object-cover"
      >
      <div class="absolute inset-0 flex items-center justify-center">
        <h1 class="text-5xl font-serif text-black">Collections</h1>
      </div>
    </section>

    <!-- Koleksi -->
    <div class="max-w-7xl mx-auto px-6 py-16">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="collection in collections" :key="collection.name" class="relative group cursor-pointer overflow-hidden rounded-lg">
          <img :src="collection.image" :alt="collection.name" class="w-full h-80 object-cover transition-transform duration-300 group-hover:scale-110">
          <div class="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
            <h3 class="font-serif text-white text-2xl font-semibold">{{ collection.name }}</h3>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const collections = [
  { name: 'Gamis', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { name: 'Koko', image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400' },
  { name: 'Abaya', image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400' },
  { name: 'Accessories', image: 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400' },
]
</script>