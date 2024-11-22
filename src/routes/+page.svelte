<script>
  import TimeCard from '$lib/components/TimeCard.svelte';
  import { fly } from 'svelte/transition'
  let time = $state(new Date());
  let date = $state(new Date());
  let wake_time = $state("00:00");
  let bed_time = $state("00:00");
  const full_date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const full_time_options = { hour: 'numeric', minute: '2-digit', hour12:false};
  setInterval(()=>{
    time = new Date()
    date = new Date()
  }, 1000)
  $inspect("wake", wake_time);
  $inspect("sleep", bed_time);
  let formattedDate = $derived(date.toLocaleDateString('en-US', full_date_options));
  let formattedTime = $derived(time.toLocaleTimeString('en-US', full_time_options));

  </script>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8" in:fly={{ x: -200, duration: 300 }} out:fly={{x:-200, duration: 300}}>
        <div class="col-span-1 md:col-span-2 text-center">
          <h1 class="text-9xl font-bold mb-2">{formattedTime}</h1>
          <h2 class="text-4xl text-gray-400 mb-10">{formattedDate}</h2>
        </div>
          <TimeCard icon_url={"sunrise.svg"} bind:time={wake_time}>Wake Up</TimeCard>

          <TimeCard icon_url={"sunset.svg"} bind:time={bed_time}>Bedtime</TimeCard>
      </div>



