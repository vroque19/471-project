<script>
  import { fly } from "svelte/transition";
</script>

<div
  class="col-span-1 md:col-span-2 text-center cursor-none select-none"
  in:fly={{ x: 200, duration: 300 }}
  out:fly={{ x: 300, duration: 300 }}
>
  Weekly Sleep Data
</div>
