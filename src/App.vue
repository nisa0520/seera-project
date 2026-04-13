<template>
  <div class="min-h-screen bg-gray-50">
    <Navbar />
    <RouterView />
    <Footer />
    <ChatbotWidget />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import ChatbotWidget from './components/chatbot/ChatbotWidget.vue'
</script>