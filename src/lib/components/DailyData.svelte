<script>
  import { fly } from "svelte/transition";
  // import { LayerCake } from "layercake";
</script>

<div
  class="col-span-1 md:col-span-2 text-center"
  in:fly={{ x: 200, duration: 300 }}
>
  Daily Sleep Data
</div>
