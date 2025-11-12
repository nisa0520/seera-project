<template>
  <div>
    <Hero />
    <Collections />
    <ProductGrid title="New Arrival" :products="newArrivals" />
    <ProductGrid title="Best Seller" :products="bestSellers" />
    <Testimonials />
  </div>
</template>

<script setup>
import Hero from '../components/Hero.vue'
import Collections from '../components/Collections.vue'
import ProductGrid from '../components/ProductGrid.vue'
import Testimonials from '../components/Testimonials.vue'

const newArrivals = [
  { id: 1, name: 'Koko Pria', price: 'Rp250.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400' },
  { id: 2, name: 'Gamis Wanita', price: 'Rp280.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { id: 3, name: 'Koko Pria', price: 'Rp290.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400' },
  { id: 4, name: 'Koko Pria', price: 'Rp200.000', discount: 'New In', image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400' },
]

const bestSellers = [
  { id: 5, name: 'Koko Pria', price: 'Rp200.000', image: 'https://images.unsplash.com/photo-1622470953794-aa9c70b0fb9d?w=400' },
  { id: 6, name: 'Gamis Wanita', price: 'Rp200.000', image: 'https://images.unsplash.com/photo-1583486932668-31780f1f5527?w=400' },
  { id: 7, name: 'Koko Pria', price: 'Rp290.000', image: 'https://images.unsplash.com/photo-1578632292335-df3abbb0d586?w=400' },
  { id: 8, name: 'Koko Pria', price: 'Rp200.000', image: 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=400' },
]
</script>