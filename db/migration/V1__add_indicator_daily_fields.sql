-- Migration V1: 扩展 indicator_daily 表，添加情绪聚合字段
-- 执行时间: 2026-03-17
-- 背景: indicator_daily 原先是空壳实体，此次添加 sentiment_daily_aggregation.csv 对应的字段

ALTER TABLE indicator_daily
    ADD COLUMN date              DATE   NOT NULL COMMENT '统计日期',
    ADD COLUMN event_count       INT    NOT NULL DEFAULT 0 COMMENT '当日事件总数',
    ADD COLUMN pos_count         INT    NOT NULL DEFAULT 0 COMMENT '正面事件数',
    ADD COLUMN neg_count         INT    NOT NULL DEFAULT 0 COMMENT '负面事件数',
    ADD COLUMN sentiment_sum     DOUBLE          COMMENT '情绪分总和',
    ADD COLUMN sentiment_mean    DOUBLE          COMMENT '情绪均值（用于模型 sentiment_index 输入）',
    ADD COLUMN max_abs_sentiment DOUBLE          COMMENT '最大绝对情绪强度',
    ADD UNIQUE KEY uk_date (date);
