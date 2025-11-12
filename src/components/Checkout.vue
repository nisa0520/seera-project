<template>
  <div class="checkout-page" style="padding: 40px;">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-10 py-24">

      <!-- LEFT -->
      <div>
        <h2 class="text-xl font-semibold mb-4">Address</h2>

        <div class="text-sm mb-4">
          Already have account?
          <router-link to="/login" class="underline">LOG IN</router-link>
        </div>

        <div class="space-y-3">
          <input class="input" placeholder="Country/Region">
          <input class="input" placeholder="Full Name">
          <input class="input" placeholder="Phone Number">
          <input class="input" placeholder="City/District">
          <textarea class="input" placeholder="Address"></textarea>
        </div>

        <h2 class="text-xl font-semibold mt-8 mb-3">Metode Pengiriman</h2>
        <input class="input" placeholder="JNE / Sicepat / dll">

        <h2 class="text-xl font-semibold mt-8 mb-3">Metode Pembayaran</h2>

        <div class="flex justify-between items-center border p-3 rounded-lg cursor-pointer">
          <img src="https://upload.wikimedia.org/wikipedia/commons/9/95/Alfamart_logo.svg"
               class="h-6">
          <span>Alfamart</span>
        </div>
      </div>

      <!-- RIGHT -->
      <div>
        <div class="border p-4 rounded-xl">
          <div class="flex items-center gap-4">
            <img src="/koko-hijau.png" class="w-28 h-32 object-cover">

            <div>
              <h3 class="font-semibold">Koko Pria</h3>
              <p>Rp200.000</p>
              <p class="text-sm text-gray-500">Hijau</p>

              <div class="flex items-center gap-2 mt-2">
                <button class="border px-3">-</button>
                <span>1</span>
                <button class="border px-3">+</button>
                <button class="text-red-500">🗑</button>
              </div>
            </div>
          </div>

          <div class="mt-4">
            <p class="text-sm text-gray-700 mb-2">Enter discount code here</p>

            <div class="flex border">
              <input 
                class="flex-1 px-3 py-2 border-r outline-none"
                placeholder="Discount code"
              >
              <button class="px-4 bg-[#b48b3c] text-black">Apply</button>
            </div>
          </div>

          <div class="mt-4 text-sm">
            <p>Subtotal • 1 Item</p>
            <p>Discount Product</p>
          </div>
        </div>

        <div class="flex justify-between mt-8 text-xl">
          <span>Total</span>
          <span>Rp200.000</span>
        </div>

        <button class="order-btn mt-6" @click="goToOrderDetail">
          Order Now
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const goToOrderDetail = () => {
  router.push('/order-detail')
}
</script>

<style>
.input {
  width: 100%;
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 6px;
}
.order-btn {
  width: 100%;
  background: #b48b37;
  color: white;
  padding: 14px;
  border-radius: 6px;
  font-size: 18px;
}
</style>
