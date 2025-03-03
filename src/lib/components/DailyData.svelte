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
  let file_name = `${year}-${month}-${day}`;
  console.log("file_name", file_name);
</script>

<div class="col-span-1 text-center pt-4 pb-4 pr-5 text-xl">
  Daily Sleep Data
</div>
<img src="/charts/{file_name}.png " alt="daily sleep data" />
