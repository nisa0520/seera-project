<template>
  <div 
    class="p-10 grid grid-cols-1 md:grid-cols-2 gap-10 py-24
           bg-white text-black dark:bg-black dark:text-gray-100 transition"
  >

    <!-- LEFT -->
    <div>
      <h1 class="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
        Your Order is Completed!
      </h1>

      <p class="text-sm mb-4 text-gray-700 dark:text-gray-300">
        ID-02901290
      </p>

      <p class="text-sm mb-6 text-gray-700 dark:text-gray-300">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor 
        incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.
      </p>

      <h2 class="font-semibold mb-2 text-gray-900 dark:text-white">
        Payment Method
      </h2>

      <p class="text-sm mb-6 text-gray-700 dark:text-gray-300">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor.
      </p>

      <h2 class="font-semibold mb-2 text-gray-900 dark:text-white">
        Shipping Address
      </h2>

      <p class="text-sm text-gray-700 dark:text-gray-300">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      </p>
    </div>

    <!-- RIGHT -->
    <div>

      <!-- PRODUCT CARD -->
      <div 
        class="border p-4 rounded-xl 
               bg-white dark:bg-gray-900
               border-gray-300 dark:border-gray-700 transition"
      >
        <div class="flex gap-4">
          <img 
            src="/koko-hijau.png" 
            class="w-28 h-32 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
          >

          <div>
            <h3 class="font-semibold text-gray-900 dark:text-white">
              Koko Pria
            </h3>

            <p class="text-gray-900 dark:text-gray-200">Rp200.000</p>

            <p class="text-sm text-gray-500 dark:text-gray-400">Hijau</p>

            <div class="flex items-center gap-2 mt-2">
              <button 
                class="border px-3 py-1 rounded 
                       bg-white dark:bg-gray-700 
                       border-gray-300 dark:border-gray-600
                       text-gray-900 dark:text-gray-100"
              >-</button>

              <span class="text-gray-900 dark:text-gray-100">1</span>

              <button 
                class="border px-3 py-1 rounded 
                       bg-white dark:bg-gray-700 
                       border-gray-300 dark:border-gray-600
                       text-gray-900 dark:text-gray-100"
              >+</button>

              <button class="text-red-500">🗑</button>
            </div>
          </div>
        </div>

        <!-- Subtotal info -->
        <div class="mt-4 text-sm text-gray-700 dark:text-gray-300">
          <p>Subtotal • 1 Item</p>
          <p>Discount Product</p>
        </div>
      </div>

      <!-- TOTAL -->
      <div class="flex justify-between mt-8 text-xl text-gray-900 dark:text-white">
        <span>Total</span>
        <span>Rp200.000</span>
      </div>

      <!-- BUTTON -->
      <router-link to="/" class="block mt-6">
        <button 
          class="w-full bg-[#b48b3c] hover:bg-[#9d7835] transition 
                 text-white p-3 rounded-lg text-lg"
        >
          Continue Shopping
        </button>
      </router-link>

    </div>

  </div>
</template>
