<template>
  <section class="section-grid">
    <h1 class="page-title">新闻与情绪 / 事件</h1>
    <p class="page-subtitle">展示近期新闻、情绪变化与关键事件信息。</p>

    <AsyncState
      :status="status"
      :error-message="errorMessage"
      empty-text="暂无新闻和事件"
      show-retry
      @retry="loadData"
    >
      <div class="grid-two">
        <NewsList :items="news" />
        <EventTimeline :items="events" />
      </div>
    </AsyncState>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import AsyncState from "@/components/common/AsyncState.vue";
import NewsList from "@/components/news/NewsList.vue";
import EventTimeline from "@/components/events/EventTimeline.vue";
import { getEventList, getNewsList } from "@/api";
import type { LoadStatus } from "@/types/common";
import type { EventItem } from "@/types/events";
import type { NewsItem } from "@/types/news";

const status = ref<LoadStatus>("loading");
const errorMessage = ref("获取新闻与事件失败");
const news = ref<NewsItem[]>([]);
const events = ref<EventItem[]>([]);

async function loadData(): Promise<void> {
  status.value = "loading";

  try {
    const [newsRes, eventRes] = await Promise.all([
      getNewsList(),
      getEventList()
    ]);

    news.value = newsRes.list;
    events.value = eventRes.list;
    status.value = newsRes.list.length || eventRes.list.length ? "success" : "empty";
  } catch (error) {
    console.error(error);
    errorMessage.value = error instanceof Error ? error.message : "获取新闻与事件失败";
    status.value = "error";
  }
}

onMounted(() => {
  void loadData();
});
</script>

<style scoped>
.grid-two {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 900px) {
  .grid-two {
    grid-template-columns: 1fr;
  }
}
</style>