# db/ — 数据库相关文件

本目录包含项目数据库的所有相关文件：DDL 变更脚本、数据导入脚本、原始数据文件和说明文档。

## 目录结构

```
db/
├── migration/          SQL DDL 变更脚本（按版本命名）
├── scripts/            Python 数据导入脚本
├── data/               原始 CSV 数据文件
└── docs/               数据库设计与操作说明
```

---

## migration/ — SQL 变更记录

| 文件 | 说明 |
|---|---|
| `V1__add_indicator_daily_fields.sql` | 为 `indicator_daily` 表添加情绪聚合字段 |

> 项目使用 `ddl-auto: none`，所有 schema 变更须手动执行 SQL。

---

## scripts/ — 数据导入脚本

依赖：`pip install mysql-connector-python`

| 文件 | 导入目标 | 说明 |
|---|---|---|
| `import_events.py` | `news_article` + `extreme_event` + `sentiment_score` | 导入事件新闻数据，每行 CSV 拆分写入三张表 |
| `import_sentiment_daily.py` | `indicator_daily` | 导入每日情绪聚合数据 |

**运行方式（从项目根目录执行）：**

```bash
python3 db/scripts/import_events.py
python3 db/scripts/import_sentiment_daily.py
```

数据库连接配置在脚本顶部的 `DB_CONFIG`，与 `application-local.yml` 保持一致。

---

## data/ — 原始数据文件

| 文件 | 行数 | 内容 |
|---|---|---|
| `event_detail.csv` | 1000 | 石油相关新闻事件（含情绪方向、强度、来源） |
| `sentiment_daily_aggregation.csv` | 1482 | 每日情绪聚合统计（2020-08-28 至 2026-03-10） |

---

## docs/ — 说明文档

| 文件 | 内容 |
|---|---|
| `数据导入说明.md` | `event_detail.csv` 字段映射与导入方式 |
| `sentiment_daily_聚合数据导入说明.md` | `indicator_daily` 表改造说明与字段映射 |
| `系统测试报告.md` | 后端与模型服务的联调测试报告（含 Bug 修复记录） |
