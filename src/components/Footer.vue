<template>
  <footer class="bg-white text-black">
    <!-- Newsletter -->
    <div class="px-4 sm:px-6 md:px-8 lg:px-24 py-8 md:py-0">
      <div
        class="bg-[#725622] py-6 sm:py-8 md:py-10 px-4 sm:px-6 md:px-12 lg:px-24 shadow-lg max-w-xs sm:max-w-2xl md:max-w-4xl mx-auto rounded-lg"
      >
        <div
          class="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-8 text-center md:text-left"
        >
          <h3 class="font-serif text-lg sm:text-xl md:text-2xl text-white">
            Subscribe Newsletters
          </h3>

          <div class="relative w-full md:flex-1">
            <input
              type="email"
              placeholder="Enter your email"
              class="px-3 sm:px-4 py-2.5 sm:py-3 md:py-4 pr-24 sm:pr-28 md:pr-32 w-full text-sm sm:text-base text-gray-700 focus:outline-none focus:ring-2 focus:ring-white rounded-md"
            />
            <button
              class="bg-[#C99F53] text-white text-xs sm:text-sm absolute right-1 top-1 bottom-1 px-2 sm:px-4 md:px-6 py-1.5 sm:py-2 font-semibold hover:bg-seera-gold transition rounded-md"
            >
              Subscribe Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Links & Socials -->
    <div class="py-8 sm:py-10 md:py-12 px-4 sm:px-6 md:px-12 lg:px-24">
      <div class="max-w-4xl mx-auto">
        <!-- Social Icons - Tampil di atas untuk mobile -->
        <div class="flex md:hidden gap-4 sm:gap-6 justify-center mb-8">
          <a href="#" class="bg-seera-gold rounded-full p-2.5 hover:bg-opacity-90">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
            </svg>
          </a>
          <a href="#" class="bg-seera-gold rounded-full p-2.5 hover:bg-opacity-90">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z" />
            </svg>
          </a>
          <a href="#" class="bg-seera-gold rounded-full p-2.5 hover:bg-opacity-90">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
            </svg>
          </a>
        </div>

        <div class="flex flex-col md:flex-row justify-between items-center md:items-start mb-8 md:mb-12 gap-6 md:gap-8">
          <!-- Links -->
          <div class="flex flex-col md:flex-row gap-3 sm:gap-4 md:gap-16 text-center md:text-left">
            <RouterLink
              to="/about"
              class="text-black text-sm sm:text-base hover:text-seera-gold transition-colors duration-300"
            >
              About
            </RouterLink>
            <RouterLink
              to="/contact"
              class="text-black text-sm sm:text-base hover:text-seera-gold transition-colors duration-300"
            >
              Contact
            </RouterLink>
            <RouterLink
              to="/term"
              class="text-black text-sm sm:text-base hover:text-seera-gold transition-colors duration-300"
            >
              Term & Conditions
            </RouterLink>
          </div>

          <!-- Social Icons - Desktop only -->
          <div class="hidden md:flex gap-6 justify-center">
            <a href="#" class="bg-seera-gold rounded-full p-3 hover:bg-opacity-90">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
              </svg>
            </a>
            <a href="#" class="bg-seera-gold rounded-full p-3 hover:bg-opacity-90">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
              </svg>
            </a>
            <a href="#" class="bg-seera-gold rounded-full p-3 hover:bg-opacity-90">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
              </svg>
            </a>
          </div>
        </div>

        <!-- Copyright & Logo -->
        <div class="flex flex-col-reverse md:flex-row justify-between items-center pt-6 md:pt-8 border-t border-gray-200 gap-4">
          <p class="text-black text-xs sm:text-sm text-center md:text-left">
            ©2025 Seera Project. All Rights Reserved.
          </p>
          <img src="/logo.svg" alt="Seera Project" class="h-12 sm:h-14 md:h-10" />
        </div>
      </div>
    </div>
  </footer>
</template>