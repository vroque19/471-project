<script>
  import TimeCard from "$lib/components/TimeCard.svelte";
  import { onMount } from "svelte";
  let time = $state(new Date());
  let date = $state(new Date());
  let wake_time = $state("06:00");
  let bed_time = $state("22:00");
  let isLoading = $state(true); // Flag to track loading state
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
  // Function to get sunrise/sunset times

  onMount(async () => {
    isLoading = true;

    // First check localStorage for user-saved preferences
    const savedWakeTime = localStorage.getItem("wake_time");
    const savedBedTime = localStorage.getItem("bed_time");

    if (savedWakeTime && savedBedTime) {
      // Use saved preferences if available
      wake_time = savedWakeTime;
      bed_time = savedBedTime;
    } else {
      // If no saved preferences, use sunrise/sunset times
      try {
        wake_time = "06:30";
        bed_time = "22:30";

        // Save these initial values to localStorage
        saveToLocalStorage();

        // You might also want to save to server
        saveSleepSetting();
      } catch (error) {
        console.error("Failed to initialize:", error);
        // Fallback values already set in state initialization
      }
    }

    isLoading = false;
  });

  function saveToLocalStorage() {
    console.log("saved to local storage", wake_time, bed_time);
    localStorage.setItem("wake_time", wake_time);
    localStorage.setItem("bed_time", bed_time);
  }
  async function saveSleepSetting() {
    try {
      saveToLocalStorage();
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
  // setInterval(() => {
  //   console.log(
  //     `Current time from JavaScript: ${new Date().toLocaleTimeString()}`,
  //   );
  // }, 1000);
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-8">
  <div class="col-span-1 md:col-span-2 text-center">
    <h1 class="text-9xl font-bold mb-2">{formattedTime}</h1>
    <h2 class="text-4xl text-gray-400 mb-10">{formattedDate}</h2>
  </div>
  <TimeCard
    icon_url={"sunset.svg"}
    bind:time={bed_time}
    onTimeUpdate={handleBedTimeUpdate}>Bedtime</TimeCard
  >
  <TimeCard
    icon_url={"sunrise.svg"}
    bind:time={wake_time}
    onTimeUpdate={handleWakeTimeUpdate}>Wake Up</TimeCard
  >
</div>
