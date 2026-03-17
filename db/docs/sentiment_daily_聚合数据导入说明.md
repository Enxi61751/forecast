# sentiment_daily_aggregation.csv 数据导入说明

## 一、数据来源

- 文件：`~/data/sentiment_daily_aggregation.csv`
- 记录数：1482 条（2020-08-28 至 2026-03-10）
- 内容：以日期为单位的情绪事件聚合统计，用于模型的 `sentiment_index` 时序输入。

原始 CSV 字段说明：

| 字段名 | 类型 | 含义 |
|---|---|---|
| date | date | 统计日期 |
| event_count | int | 当日事件总数 |
| pos_count | int | 正面（利多）事件数量 |
| neg_count | int | 负面（利空）事件数量 |
| sentiment_sum | float | 当日情绪分总和 |
| sentiment_mean | float | 当日情绪均值 |
| max_abs_sentiment | float | 当日最大绝对情绪强度 |

---

## 二、数据库改造：扩展 `indicator_daily` 表

### 2.1 改造前的状态

`indicator_daily` 原先是一个**空壳实体**，只有主键字段：

```sql
-- 改造前
CREATE TABLE indicator_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY
);
```

对应的 Java 实体（`IndicatorDaily.java`）也只有 `id` 字段。

### 2.2 为什么存入 `indicator_daily` 而非新建表

该表命名为"每日指标"，语义上与情绪聚合数据完全匹配：
- 聚合数据是**每天一行**，与表的粒度一致
- 模型 `pipeline.py` 需要 `sentiment_index` 作为时序输入，这正是 `sentiment_mean` 的用途
- 扩展现有表比新建表更简洁，也避免增加不必要的表数量

### 2.3 执行的 ALTER TABLE SQL

```sql
ALTER TABLE indicator_daily
    ADD COLUMN date DATE NOT NULL COMMENT '统计日期',
    ADD COLUMN event_count INT NOT NULL DEFAULT 0 COMMENT '当日事件总数',
    ADD COLUMN pos_count INT NOT NULL DEFAULT 0 COMMENT '正面事件数',
    ADD COLUMN neg_count INT NOT NULL DEFAULT 0 COMMENT '负面事件数',
    ADD COLUMN sentiment_sum DOUBLE COMMENT '情绪分总和',
    ADD COLUMN sentiment_mean DOUBLE COMMENT '情绪均值',
    ADD COLUMN max_abs_sentiment DOUBLE COMMENT '最大绝对情绪强度',
    ADD UNIQUE KEY uk_date (date);
```

`date` 字段加了**唯一键约束**，防止同一天被重复导入。

### 2.4 同步修改的 Java 实体

文件：`src/main/java/com/citicup/entity/IndicatorDaily.java`

```java
@Entity
@Table(name = "indicator_daily")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class IndicatorDaily {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private LocalDate date;

    @Column(name = "event_count", nullable = false)
    private Integer eventCount;

    @Column(name = "pos_count", nullable = false)
    private Integer posCount;

    @Column(name = "neg_count", nullable = false)
    private Integer negCount;

    @Column(name = "sentiment_sum")
    private Double sentimentSum;

    @Column(name = "sentiment_mean")
    private Double sentimentMean;

    @Column(name = "max_abs_sentiment")
    private Double maxAbsSentiment;
}
```

---

## 三、字段映射

| 数据库字段 | CSV 字段 | 说明 |
|---|---|---|
| `date` | `date` | 统计日期，唯一键 |
| `event_count` | `event_count` | 当日事件总数 |
| `pos_count` | `pos_count` | 正面事件数 |
| `neg_count` | `neg_count` | 负面事件数 |
| `sentiment_sum` | `sentiment_sum` | 情绪分总和 |
| `sentiment_mean` | `sentiment_mean` | 情绪均值（供模型使用） |
| `max_abs_sentiment` | `max_abs_sentiment` | 最大绝对情绪强度 |

---

## 四、导入脚本

脚本位置：`~/data/import_sentiment_daily.py`

执行方式：
```bash
python3 ~/data/import_sentiment_daily.py
```

导入逻辑：
- 直接逐行写入 `indicator_daily`
- 遇到日期重复（`IntegrityError`）时跳过，不报错

---

## 五、导入结果验证

```sql
-- 验证总行数（应为 1482）
SELECT COUNT(*) FROM indicator_daily;

-- 查看最新 5 天的数据
SELECT date, event_count, pos_count, neg_count, sentiment_mean, max_abs_sentiment
FROM indicator_daily
ORDER BY date DESC
LIMIT 5;
```

---

## 六、数据在模型中的用途

模型服务（`model-remote` 分支）的 `PredictRequest` 接收 `series.sentiment_index` 字段：

```python
class SeriesPayload(BaseModel):
    price: List[TimePoint]
    indicators: Dict[str, List[TimePoint]]
    sentiment_index: Optional[List[TimePoint]]  # ← 对应 sentiment_mean 字段
```

构建预测请求时，从 `indicator_daily` 表查出指定日期范围内的 `sentiment_mean`，
按时间组装成 `[{"t": "2026-03-01T00:00:00Z", "v": 0.914}, ...]` 格式传入模型。
