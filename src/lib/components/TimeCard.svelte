<script>
  import { flip } from "svelte/animate";
  import SveltyPicker from "svelty-picker";
  import { currentPage } from "../../app.svelte.js";

  let {
    icon_url,
    time = $bindable(),
    onTimeUpdate = $bindable(() => {}),
  } = $props();
  let showTimePicker = $state(false);
  const url_icon_prefix = "https://unpkg.com/lucide-static@latest/icons/";
  function toggleTimePicker() {
    if (!showTimePicker) showTimePicker = !showTimePicker;
  }
  function updateTime() {
    showTimePicker = false;
    console.log(time);
    onTimeUpdate(time);
  }
</script>

<div class="space-y-2">
  <div class="flex items-center space-x-6">
    <!-- wake up  -->
    <img
      src={url_icon_prefix + icon_url}
      width="40"
      height="40"
      style="filter:invert(1)"
      alt="sun icon"
    />
    <div class="relative">
      <p class="text-2xl text-semibold"><slot></slot></p>
      <p class="text-6xl" onclick={toggleTimePicker}>{time}</p>
      {#if showTimePicker}
        <span class="h-screen w-screen inset-0 fixed" onclick={updateTime}>
        </span>
        <span id="wrapping" class="absolute bottom-3 right-1">
          <span class="min-w-96 min-h-96 bg-green-400"></span>
          <SveltyPicker
            bind:value={time}
            pickerOnly={true}
            format="hh:ii"
            displayFormat="HH:ii P"
          />
        </span>
      {/if}
    </div>
  </div>
</div>
