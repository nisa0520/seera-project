<template>
  <footer class="bg-white text-black">
    <!-- Newsletter -->
    <div
      class="bg-[#725622] py-10 px-6 sm:px-12 md:px-24 shadow-lg max-w-4xl mx-auto rounded-lg"
    >
      <div
        class="flex flex-col md:flex-row items-center justify-between gap-6 md:gap-8 text-center md:text-left"
      >
        <h3 class="font-serif text-2xl text-white">
          Subscribe Newsletters
        </h3>

        <div class="relative w-full md:flex-1">
          <input
            type="email"
            placeholder="Enter your email"
            class="px-4 py-3 md:py-4 pr-32 w-full text-gray-700 focus:outline-none focus:ring-2 focus:ring-white rounded-md"
          />
          <button
            class="bg-[#C99F53] text-white absolute right-1 top-1 bottom-1 px-4 md:px-6 py-2 font-semibold hover:bg-seera-gold transition rounded-md"
          >
            Subscribe Now
          </button>
        </div>
      </div>
    </div>

    <!-- Links & Socials -->
    <div class="py-12 px-6 sm:px-12 md:px-24">
      <div class="max-w-4xl mx-auto">
        <div
          class="flex flex-col md:flex-row justify-between items-center md:items-start mb-12 gap-8"
        >
          <!-- Links -->
          <div
            class="flex flex-col md:flex-row gap-4 md:gap-16 text-center md:text-left"
          >
            <RouterLink
              to="/about"
              class="text-black hover:text-seera-gold transition-colors duration-300"
            >
              About
            </RouterLink>
            <RouterLink
              to="/contact"
              class="text-black hover:text-seera-gold transition-colors duration-300"
            >
              Contact
            </RouterLink>
            <RouterLink
              to="/term"
              class="text-black hover:text-seera-gold transition-colors duration-300"
            >
              Term & Conditions
            </RouterLink>
          </div>

          <!-- Social Icons -->
          <div class="flex gap-6 justify-center">
            <a href="#" class="bg-seera-gold rounded-full p-3 hover:bg-opacity-90">
              <svg
                class="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
                />
              </svg>
            </a>
            <a href="#" class="bg-seera-gold rounded-full p-3 hover:bg-opacity-90">
              <svg
                class="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"
                />
              </svg>
            </a>
            <a href="#" class="bg-seera-gold rounded-full p-3 hover:bg-opacity-90">
              <svg
                class="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"
                />
              </svg>
            </a>
          </div>
        </div>

        <!-- Copyright -->
        <div
          class="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-gray-200 gap-4"
        >
          <p class="text-black text-sm text-center md:text-left">
            ©2025 Seera Project. All Rights Reserved.
          </p>
          <img src="/logo.svg" alt="Seera Project" class="h-10" />
        </div>
      </div>
    </div>
  </footer>
</template>
