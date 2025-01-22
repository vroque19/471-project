<script>
  import "../app.css";
  import { fly } from "svelte/transition";
  import {
    handleTouchStart,
    handleTouchEnd,
    currentPage,
  } from "../app.svelte.js";
</script>

<div
  class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white flex items-center justify-center p-4 cursor-none"
  on:touchstart={handleTouchStart}
  on:touchend={handleTouchEnd}
  in:fly={{ x: 200, duration: 300 }}
>
  <div
    class="bg-gray-800 rounded-3xl shadow-2xl p-8 max-w-2xl w-full mx-auto h-full"
  >
    <slot />
    <!-- <h1>Page: {$currentPage}</h1> -->
  </div>
</div>

<style>
  .fly-enter {
    position: absolute;
  }
</style>
