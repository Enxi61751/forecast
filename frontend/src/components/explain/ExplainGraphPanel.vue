<template>
  <section class="card explain-card">
    <header class="head">
      <h3>图结构可视化</h3>
      <p v-if="hoverText">{{ hoverText }}</p>
      <p v-else>将鼠标移动到连线上可查看关系权重</p>
    </header>

    <svg viewBox="0 0 460 300" class="graph-svg">
      <line
        v-for="(edge, index) in edges"
        :key="`edge-${index}`"
        :x1="findNode(edge.from)?.x || 0"
        :y1="findNode(edge.from)?.y || 0"
        :x2="findNode(edge.to)?.x || 0"
        :y2="findNode(edge.to)?.y || 0"
        :stroke-width="1 + edge.weight * 2"
        stroke="rgba(149, 182, 255, 0.58)"
        @mouseenter="hoverText = `${edge.from} -> ${edge.to} 权重 ${edge.weight.toFixed(2)}`"
        @mouseleave="hoverText = ''"
      />

      <g v-for="node in nodes" :key="node.id">
        <circle :cx="node.x" :cy="node.y" r="22" :fill="node.color" fill-opacity="0.9" />
        <text :x="node.x" :y="node.y + 38" text-anchor="middle" fill="#d6e2ff" font-size="12">{{ node.label }}</text>
      </g>
    </svg>

    <footer class="legend">
      <span v-for="node in nodes" :key="`legend-${node.id}`">
        <i :style="{ background: node.color }" />
        {{ node.label }}
      </span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { GraphEdge, GraphNode } from "@/mocks/explain";

const props = defineProps<{
  nodes: GraphNode[];
  edges: GraphEdge[];
}>();

const hoverText = ref("");

function findNode(id: string): GraphNode | undefined {
  return props.nodes.find((node) => node.id === id);
}
</script>

<style scoped>
.explain-card {
  padding: 16px;
}

.head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.head h3 {
  margin: 0;
}

.head p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.graph-svg {
  width: 100%;
  min-height: 360px;
  margin-top: 10px;
  border: 1px solid rgba(132, 161, 255, 0.22);
  border-radius: var(--radius-md);
  background: rgba(7, 13, 30, 0.72);
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}

.legend span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.legend i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
</style>
