<template>
  <section class="card hero-wrap">
    <div class="hero-glow" />
    <div class="hero-text">
      <p class="kicker">Financial Risk Intelligence</p>
      <h1>金融风险预测与解释展示平台</h1>
      <p>
        聚合新闻情绪、极端事件、市场行情、预测结果和多智能体解释输出，
        为当前项目提供可展示、可扩展、可继续对接后端的前端承接层。
      </p>
    </div>
  </section>
</template>

<style scoped>
.hero-wrap {
  position: relative;
  overflow: hidden;
  padding: 36px;
  min-height: 280px;
}

.hero-glow {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 30%, rgba(79, 130, 255, 0.32), transparent 38%),
    radial-gradient(circle at 70% 70%, rgba(106, 94, 255, 0.35), transparent 42%),
    linear-gradient(125deg, rgba(7, 15, 39, 0.7), rgba(14, 21, 46, 0.45));
  animation: heroShift 7s ease-in-out infinite alternate;
}

.hero-text {
  position: relative;
  max-width: 640px;
}

.kicker {
  margin: 0 0 10px;
  color: #86d0ff;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 12px;
}

h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.2;
}

p {
  margin: 16px 0 0;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

@keyframes heroShift {
  from {
    transform: scale(1);
  }
  to {
    transform: scale(1.03);
  }
}

@media (max-width: 768px) {
  .hero-wrap {
    padding: 24px;
    min-height: 240px;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
