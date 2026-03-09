<template>
  <section class="card chart-panel">
    <header class="panel-head">
      <h3>{{ title }}</h3>
      <slot name="head-extra" />
    </header>

    <div class="chart-box" :style="{ height: `${height}px` }" ref="chartBoxRef">
      <svg
        v-if="points.length > 1"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        role="img"
        aria-label="trend chart"
        @mousemove="onMouseMove"
        @mouseleave="onMouseLeave"
      >
        <defs>
          <linearGradient :id="gradientId" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="rgba(93, 144, 255, 0.58)" />
            <stop offset="100%" stop-color="rgba(93, 144, 255, 0.06)" />
          </linearGradient>
        </defs>

        <polyline class="line" :points="pointString" />
        <polygon class="area" :points="areaString" :fill="`url(#${gradientId})`" />

        <g v-if="hoverPoint">
          <line class="pointer-line pointer-x" :x1="hoverPoint.x" y1="8" :x2="hoverPoint.x" y2="92" />
          <line class="pointer-line pointer-y" x1="0" :y1="hoverPoint.y" x2="100" :y2="hoverPoint.y" />
          <circle class="focus-dot" :cx="hoverPoint.x" :cy="hoverPoint.y" r="1.9" />
        </g>
      </svg>

      <div v-else class="chart-empty">暂无图表数据</div>

      <div v-if="hoverPoint" class="chart-tooltip" :style="tooltipStyle">
        <p>{{ hoverPoint.label }}</p>
        <strong>{{ formatValue(hoverPoint.value) }}</strong>
      </div>
    </div>

    <div class="labels" v-if="displayLabels.length">
      <span v-for="(label, index) in displayLabels" :key="`${label}-${index}`">{{ label }}</span>
    </div>

    <div v-if="showZoomControls" class="zoom-controls">
      <label>
        起点 {{ displayStart + 1 }}
        <input type="range" :min="0" :max="Math.max(values.length - 2, 0)" v-model.number="zoomStart" />
      </label>
      <label>
        终点 {{ displayEnd + 1 }}
        <input type="range" :min="Math.min(zoomStart + 1, Math.max(values.length - 1, 1))" :max="Math.max(values.length - 1, 1)" v-model.number="zoomEnd" />
      </label>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

interface ChartPoint {
  x: number;
  y: number;
  label: string;
  value: number;
}

const props = withDefaults(
  defineProps<{
    title: string;
    labels: string[];
    values: number[];
    height?: number;
    enableZoom?: boolean;
    decimals?: number;
  }>(),
  {
    height: 250,
    enableZoom: false,
    decimals: 4
  }
);

const gradientId = `chart-fill-${Math.random().toString(36).slice(2, 8)}`;
const chartBoxRef = ref<HTMLElement | null>(null);
const zoomStart = ref(0);
const zoomEnd = ref(1);
const hoverIndex = ref<number | null>(null);

watch(
  () => props.values.length,
  (length) => {
    zoomStart.value = 0;
    zoomEnd.value = Math.max(length - 1, 1);
    hoverIndex.value = null;
  },
  { immediate: true }
);

watch(zoomStart, (start) => {
  const maxEnd = Math.max(props.values.length - 1, 1);
  if (zoomEnd.value <= start) {
    zoomEnd.value = Math.min(start + 1, maxEnd);
  }
});

const showZoomControls = computed(() => props.enableZoom && props.values.length > 6);

const displayStart = computed(() => {
  if (!showZoomControls.value) return 0;
  return Math.max(0, Math.min(zoomStart.value, Math.max(props.values.length - 2, 0)));
});

const displayEnd = computed(() => {
  if (!showZoomControls.value) return Math.max(props.values.length - 1, 0);
  const minEnd = displayStart.value + 1;
  const maxEnd = Math.max(props.values.length - 1, 1);
  return Math.max(minEnd, Math.min(zoomEnd.value, maxEnd));
});

const displayValues = computed(() => props.values.slice(displayStart.value, displayEnd.value + 1));
const displayLabels = computed(() => {
  const labels = props.labels.slice(displayStart.value, displayEnd.value + 1);
  if (labels.length === displayValues.value.length) {
    return labels;
  }
  return displayValues.value.map((_, index) => `P${index + 1}`);
});

const points = computed<ChartPoint[]>(() => {
  const values = displayValues.value;
  if (!values.length) return [];

  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;

  return values.map((value, index) => ({
    x: (index / Math.max(values.length - 1, 1)) * 100,
    y: 100 - ((value - min) / span) * 80 - 10,
    label: displayLabels.value[index] ?? `P${index + 1}`,
    value
  }));
});

const pointString = computed(() => points.value.map((point) => `${point.x},${point.y}`).join(" "));
const areaString = computed(() => {
  if (!points.value.length) return "";
  return `0,100 ${points.value.map((point) => `${point.x},${point.y}`).join(" ")} 100,100`;
});

const hoverPoint = computed(() => {
  if (hoverIndex.value === null) return null;
  return points.value[hoverIndex.value] ?? null;
});

const tooltipStyle = computed(() => {
  if (!hoverPoint.value) return {};
  const left = Math.max(10, Math.min(90, hoverPoint.value.x));
  const top = Math.max(8, hoverPoint.value.y - 7);

  return {
    left: `${left}%`,
    top: `${top}%`
  };
});

function onMouseMove(event: MouseEvent): void {
  if (!chartBoxRef.value || points.value.length === 0) return;
  const rect = chartBoxRef.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const ratio = x / rect.width;
  const index = Math.round(ratio * (points.value.length - 1));
  hoverIndex.value = Math.max(0, Math.min(index, points.value.length - 1));
}

function onMouseLeave(): void {
  hoverIndex.value = null;
}

function formatValue(value: number): string {
  return value.toFixed(props.decimals);
}
</script>

<style scoped>
.chart-panel {
  padding: 16px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.panel-head h3 {
  margin: 0;
  font-size: 16px;
}

.chart-box {
  position: relative;
  border: 1px solid rgba(129, 159, 255, 0.2);
  border-radius: var(--radius-md);
  background: rgba(6, 11, 26, 0.52);
  padding: 10px;
}

svg {
  width: 100%;
  height: 100%;
}

.line {
  fill: none;
  stroke: #7db0ff;
  stroke-width: 1.1;
}

.area {
  opacity: 0.9;
}

.pointer-line {
  stroke: rgba(153, 183, 255, 0.45);
  stroke-width: 0.45;
  stroke-dasharray: 1 1.2;
}

.focus-dot {
  fill: #d9e8ff;
  stroke: #5f91ff;
  stroke-width: 0.6;
}

.chart-tooltip {
  position: absolute;
  transform: translate(-50%, -120%);
  min-width: 98px;
  border-radius: 10px;
  border: 1px solid rgba(129, 160, 255, 0.48);
  background: rgba(8, 14, 34, 0.94);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.36);
  padding: 8px 10px;
  pointer-events: none;
}

.chart-tooltip p {
  margin: 0 0 4px;
  color: var(--color-text-secondary);
  font-size: 12px;
}

.chart-tooltip strong {
  color: #d8e6ff;
  font-size: 13px;
}

.chart-empty {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}

.labels {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(44px, 1fr));
  gap: 8px;
  margin-top: 10px;
}

.labels span {
  color: var(--color-text-muted);
  font-size: 12px;
  text-align: center;
}

.zoom-controls {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.zoom-controls label {
  display: grid;
  gap: 6px;
  color: var(--color-text-secondary);
  font-size: 12px;
}

.zoom-controls input[type="range"] {
  width: 100%;
  accent-color: #7ea7ff;
}
</style>
