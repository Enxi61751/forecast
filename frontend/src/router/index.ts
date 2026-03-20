import { createRouter, createWebHistory } from "vue-router";
import HomePage from "@/pages/HomePage.vue";
import ExchangePage from "@/pages/ExchangePage.vue";
import ForecastPage from "@/pages/ForecastPage.vue";
import NewsEventsPage from "@/pages/NewsEventsPage.vue";
import ExplainabilityPage from "@/pages/ExplainabilityPage.vue";
import NotFoundPage from "@/pages/NotFoundPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomePage, meta: { title: "首页" } },
    { path: "/exchange", name: "exchange", component: ExchangePage, meta: { title: "实时原油价格" } },
    { path: "/forecast", name: "forecast", component: ForecastPage, meta: { title: "原油价格预测" } },
    { path: "/news-events", name: "news-events", component: NewsEventsPage, meta: { title: "新闻与事件" } },
    { path: "/explainability", name: "explainability", component: ExplainabilityPage, meta: { title: "可解释性分析" } },
    { path: "/:pathMatch(.*)*", name: "not-found", component: NotFoundPage, meta: { title: "页面不存在" } }
  ]
});

router.afterEach((to) => {
  const title = typeof to.meta.title === "string" ? to.meta.title : "金融风险预测系统";
  document.title = `${title} | 金融风险预测系统`;
});

export default router;
