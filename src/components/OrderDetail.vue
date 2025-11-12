<template>
  <div class="p-10 grid grid-cols-1 md:grid-cols-2 gap-10 py-24">

    <!-- LEFT -->
    <div>
      <h1 class="text-xl font-semibold mb-2">Your Order is Completed!</h1>
      <p class="text-sm mb-4">ID-02901290</p>

      <p class="text-sm mb-6">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor 
        incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.
      </p>

      <h2 class="font-semibold mb-2">Payment Method</h2>
      <p class="text-sm mb-6">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor.
      </p>

      <h2 class="font-semibold mb-2">Shipping Address</h2>
      <p class="text-sm">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      </p>
    </div>

    <!-- RIGHT -->
    <div>
      <div class="border p-4 rounded-xl">
        <div class="flex gap-4">
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

        <div class="mt-4 text-sm">
          <p>Subtotal • 1 Item</p>
          <p>Discount Product</p>
        </div>
      </div>

      <div class="flex justify-between mt-8 text-xl">
        <span>Total</span>
        <span>Rp200.000</span>
      </div>

      <router-link to="/" class="block mt-6">
        <button class="w-full bg-[#b48b3c] text-white p-3 rounded-lg text-lg">
          Continue Shopping
        </button>
      </router-link>

    </div>
  </div>
</template>
