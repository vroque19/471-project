<script>
  import { direction } from '../../app.svelte.js';

  import { fly } from 'svelte/transition';
</script>
<div class="col-span-1 md:col-span-2 text-center" in:fly={{ x: 200, duration: 300 }}>
  Daily Sleep Data

</div>
