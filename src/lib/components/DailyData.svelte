<script>
  import { scaleLinear } from "d3-scale";
  import { Chart, Svg, Axis, Highlight, Spline, Tooltip } from "layerchart";
  let { data } = $props();
  async function loadData() {
    const response = await fetch("http://localhost:8000/api/sensor_data");
    if (!response.ok) {
      throw new Error("Failed to load sleep data");
    }
    data = await response.json();
  }
  const y1Scale = scaleLinear().domain([0, 1]); // Motion is 0 or 1

  // import { LayerCake } from "layercake";
</script>

<div
  class="col-span-1 md:col-span-2 text-center border-2 border-red-500 bg-slate-50 text-stone-950"
>
  Daily Sleep Data
</div>
<div class="col-span-1 border-2 border-orange-400 w-[800px] h-[450px]">
  <Chart
    {data}
    x="time"
    y="light(lx)"
    yDomain={[0, null]}
    yNice
    y1="motion"
    y1Scale={scaleLinear()}
    y1Range={({ yScale }) => yScale.domain()}
    padding={{ top: 24, bottom: 24, left: 24, right: 24 }}
    tooltip={{ mode: "bisect-x" }}
    let:height
    let:y1Scale
  >
    <Svg>
      <Axis
        placement="left"
        rule
        format="metric"
        label="Light (lx)"
        labelPlacement="start"
      />
      <Axis
        placement="right"
        scale={scaleLinear(y1Scale?.domain() ?? [], [height, 0])}
        ticks={y1Scale?.ticks?.()}
        rule
        label="Motion detected"
        labelPlacement="start"
      />
      <Axis placement="bottom" format="none" rule label="Time" />
      <!-- Light spline -->
      <Spline class="stroke-2 stroke-blue-500" />

      <!-- Motion spline -->
      <Spline y={(d) => y1Scale?.(d.motion)} class="stroke-2 stroke-red-500" />
      <Highlight lines points />
      <Highlight
        points={{ class: "fill-red-600" }}
        y={(d) => y1Scale?.(d.motion)}
      />
    </Svg>

    <Tooltip.Root let:data>
      <Tooltip.Header>{data.time}</Tooltip.Header>
      <Tooltip.List>
        <Tooltip.Item label="Light" value={data.light} format="none" />
        <Tooltip.Item label="Motion" value={data.motion} />
      </Tooltip.List>
    </Tooltip.Root>
  </Chart>
</div>
