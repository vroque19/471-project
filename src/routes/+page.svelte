<script>
  import TimeCard from "$lib/components/TimeCard.svelte";
  import { onMount } from "svelte";
  // import { db, settings } from "../lib/db.js";
  let time = $state(new Date());
  let date = $state(new Date());
  let wake_time = $state("00:00");
  let bed_time = $state("00:00");
  $inspect("wake", wake_time);
  $inspect("sleep", bed_time);

  const full_date_options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  const full_time_options = {
    hour: "numeric",
    minute: "2-digit",
    hour12: false,
  };

  let formattedDate = $derived(
    date.toLocaleDateString("en-US", full_date_options),
  );
  let formattedTime = $derived(
    time.toLocaleTimeString("en-US", full_time_options),
  );

  async function saveSleepSetting() {
    try {
      const response = await fetch("http://localhost:8000/api/settings", {
        // Note the new URL
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bed_time: bed_time,
          wake_time: wake_time,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to save sleep setting");
      }

      const data = await response.json();
      console.log("Sleep setting saved successfully:", data);
    } catch (error) {
      console.error("Error saving sleep setting:", error);
    }
  }
  // Callback functions for TimeCard updates
  function handleWakeTimeUpdate(newTime) {
    wake_time = newTime;
    saveSleepSetting();
  }

  function handleBedTimeUpdate(newTime) {
    bed_time = newTime;
    saveSleepSetting();
  }

  setInterval(() => {
    time = new Date();
    date = new Date();
  }, 1000);
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
  <div class="col-span-1 md:col-span-2 text-center">
    <h1 class="text-9xl font-bold mb-2">{formattedTime}</h1>
    <h2 class="text-4xl text-gray-400 mb-10">{formattedDate}</h2>
  </div>
  <TimeCard
    icon_url={"sunrise.svg"}
    bind:time={wake_time}
    onTimeUpdate={handleWakeTimeUpdate}>Wake Up</TimeCard
  >

  <TimeCard
    icon_url={"sunset.svg"}
    bind:time={bed_time}
    onTimeUpdate={handleBedTimeUpdate}>Bedtime</TimeCard
  >
</div>
