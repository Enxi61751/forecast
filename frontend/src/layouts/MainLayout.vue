<template>
  <div class="app-shell">
    <Navbar />
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import Navbar from "@/components/layout/Navbar.vue";
</script>
