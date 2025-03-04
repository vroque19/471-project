<script>
  import { direction } from "../../app.svelte.js";
  import DailyData from "$lib/components/DailyData.svelte";
</script>

<div
  class="grid grid-cols-1 place-content-center w-[800px] h-[480px] rounded-3xl shadow-2xl -mt-20 z-0 -ml-10"
>
  <!-- border for dev -->
  <DailyData />
</div>
