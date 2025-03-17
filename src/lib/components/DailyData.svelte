<script>
  let date = $state(new Date());
  console.log("date", date);
  const date_options = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  };
  let formattedDate = $derived(date.toLocaleDateString("en-US", date_options));
  let year = $derived(date.getFullYear());
  let month = formattedDate.slice(0, 2);
  let day = formattedDate.slice(3, 5);
  let file_name = `${year}-${month}-${day}-daily`;
  console.log("file_name", file_name);
  let imageNotFound = false;
</script>

<div class="text-center text-2xl -ml-20 -mb-10 z-10">Daily Sleep Data</div>
<div class="flex justify-center -mb-1">
  {#if !imageNotFound}
    <img
      src={`/charts/${file_name}.png`}
      alt="daily sleep data"
      on:error={() => (imageNotFound = true)}
    />
  {:else}
    <div class="flex items-center justify-center h-64 text-xl text-gray-500">
      No Sleep Data
    </div>
  {/if}
</div>
