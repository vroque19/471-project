<script>
  import SveltyPicker from 'svelty-picker';
  let showTimePicker = false;
  let timePicker;
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white flex items-center justify-center p-4">
  <div class="bg-gray-800 rounded-3xl shadow-2xl p-8 max-w-2xl w-full mx-auto">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div class="col-span-1 md:col-span-2 text-center">
        <h1 class="text-9xl font-bold mb-2">09:00</h1>
        <h2 class="text-4xl text-gray-400">Sunday, October 20, 2024</h2>
        
      </div>
      <div class="space-y-2">
        <div class="flex items-center space-x-6">
          <!-- wake up  -->
          <img src="https://unpkg.com/lucide-static@latest/icons/sunrise.svg"
          width="40"
          height="40"
          style="filter:invert(1)"
          alt="sunrise icon"/>
          <div class="relative">
            <p class="text-2xl text-semibold">Wake Up</p>
            <p class="text-6xl" onclick={() => showTimePicker = !showTimePicker}>7:00AM</p>
            {#if showTimePicker}
            <span id="wrapping" class="absolute bottom-3 left-5">
              <span class="min-w-96 min-h-96 bg-green-400"></span>
              <SveltyPicker bind:this={timePicker} pickerOnly={true} format="hh:ii" displayFormat="HH:ii P"/>
            </span>
            {/if}
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <!-- thermometer -->
          <img src="https://unpkg.com/lucide-static@latest/icons/thermometer.svg"
          width="40"
          height="40"
          style="filter:invert(1)"
          alt="thermometer icon"/>
          <div>
            <p class="text-2xl text-semibold">Temperature</p>
            <p class="text-4xl">70º</p>
          </div>
        </div>
      </div>
      
      <div class="space-y-2">
        <div class="flex items-center space-x-6">
          <!-- sunset -->
          <img src="https://unpkg.com/lucide-static@latest/icons/sunset.svg"
          width="40"
          height="40"
          style="filter:invert(1)"
          alt="sunset icon"/>
          <div>
            <p class="text-2xl text-semibold">Bedtime</p>
            <p class="text-6xl">11:00PM</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

