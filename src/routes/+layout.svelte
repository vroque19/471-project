<script>
  import "../app.css";
  import { fly, crossfade } from "svelte/transition";
  let isMenuOpen = $state(false);
  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }
  import {
    handleTouchStart,
    handleTouchEnd,
    currentPage,
  } from "../app.svelte.js";

  let { children, data } = $props();

  const animation_delay_ms = 150;
</script>

<div
  class="min-h-screen bg-gradient-to-br bg-gray-950 text-white flex items-center justify-center p-1 select-none cursor-none"
  on:touchstart={handleTouchStart}
  on:touchend={handleTouchEnd}
>
  <div
    class="bg-gray-820 rounded-3xl shadow-2xl p-4 max-w-2xl w-[800px] h-[480px] mx-auto overflow"
  >
    <nav class=" w-1/6">
      <div
        class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto"
      >
        <button
          data-collapse-toggle="navbar-hamburger"
          type="button"
          class="inline-flex items-center justify-center p-2 w-10 h-10 text-sm text-gray-500 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
          aria-controls="navbar-hamburger"
          aria-expanded="false"
          on:click={toggleMenu}
        >
          <span class="sr-only">Open main menu</span>
          <svg
            class="w-5 h-5"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 17 14"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M1 1h15M1 7h15M1 13h15"
            />
          </svg>
        </button>
        {#if isMenuOpen}
          <div class="w-screen bg-yellow-50" id="navbar-hamburger">
            <ul
              class="flex flex-col fixed font-medium mt-4 rounded-lg dark:bg-gray-800 dark:border-gray-700"
            >
              <li>
                <a
                  href="/"
                  class="block py-2 px-3 text-white rounded-sm dark:bg-gray-600"
                  aria-current="page">Home</a
                >
              </li>
              <li>
                <a
                  href="daily"
                  class="block py-2 px-3 text-white rounded-sm hover:bg-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                  >Daily Sleep Score</a
                >
              </li>
              <li>
                <a
                  href="weekly"
                  class="block py-2 px-3 text-white rounded-sm hover:bg-gray-600 dark:text-gray-400 md:dark:hover:text-white dark:hover:bg-gray-700 dark:hover:text-white"
                  >Weekly Sleep Data</a
                >
              </li>
            </ul>
          </div>
        {/if}
      </div>
    </nav>
    {#key data.url}
      <div
        in:fly={{
          x: 300,
          duration: animation_delay_ms,
          delay: animation_delay_ms,
        }}
        out:fly={{ x: -300, duration: animation_delay_ms }}
      >
        {@render children()}
      </div>
    {/key}
  </div>
</div>
