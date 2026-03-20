# LCO1 伦敦布伦特原油期货历史数据导入说明

## 概述

本次导入将 LCO1（伦敦布伦特原油期货）日线 OHLCV 历史数据从 Excel 文件写入 MySQL，
供后端模型服务和 API 查询使用。

- **数据量**：5386 条（2006-01-03 至 2026-02-20）
- **数据来源**：`db/data/LCO1-伦敦布伦特原油期货历史数据.xlsx`
- **目标表**：`oil_price_daily_ohlcv`

---

## 新建数据库表

### 表结构（`oil_price_daily_ohlcv`）

| 列名          | 类型         | 说明                                     |
|---------------|--------------|------------------------------------------|
| `id`          | BIGINT PK    | 自增主键                                 |
| `symbol`      | VARCHAR(20)  | 品种代码，当前固定为 `LCO1`              |
| `trade_date`  | DATE         | 交易日期，与 `symbol` 联合唯一           |
| `open_price`  | DOUBLE       | 开盘价（美元/桶）                        |
| `close_price` | DOUBLE       | 收盘价（美元/桶）                        |
| `high_price`  | DOUBLE       | 最高价（美元/桶）                        |
| `low_price`   | DOUBLE       | 最低价（美元/桶）                        |
| `volume`      | VARCHAR(20)  | 交易量（原始字符串，如 `294.58K`）       |
| `change_pct`  | DOUBLE       | 涨跌幅（小数，0.0014 表示 +0.14%）      |

**唯一约束**：`(symbol, trade_date)`，防止重复导入。

### Excel 列到数据库列的映射

| Excel 列（中文） | Excel 列顺序 | 数据库列        |
|------------------|-------------|-----------------|
| 日期             | A           | `trade_date`    |
| 收盘             | B           | `close_price`   |
| 开盘             | C           | `open_price`    |
| 高               | D           | `high_price`    |
| 低               | E           | `low_price`     |
| 交易量           | F           | `volume`        |
| 涨跌幅           | G           | `change_pct`    |

---

## 执行步骤

### 第一步：建表

```bash
mysql -h 123.206.104.63 -P 3306 -u citicup_user -pciticup123456 citicup \
    < db/migration/V2__create_oil_price_daily_ohlcv.sql
```

### 第二步：导入数据

```bash
# 安装依赖（一次性）
pip install openpyxl mysql-connector-python

# 从项目根目录执行
python3 db/scripts/import_lco1_ohlcv.py
```

预期输出：

```
完成：成功导入 5386 条，跳过重复 0 条。
```

重复执行时所有行会因唯一键冲突被跳过，不会写入重复数据。

---

## 涉及的后端改动

### 新增 JPA 实体

`src/main/java/com/citicup/entity/OilPriceDailyOhlcv.java`

对应 `oil_price_daily_ohlcv` 表，字段与表列一一对应。

### 新增 Repository

`src/main/java/com/citicup/repository/OilPriceDailyOhlcvRepo.java`

提供以下查询方法：

| 方法                                                                          | 说明                         |
|-------------------------------------------------------------------------------|------------------------------|
| `findBySymbolOrderByTradeDateAsc(String symbol)`                              | 按品种查全量数据（升序）     |
| `findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(String, LocalDate, LocalDate)` | 按品种+日期范围查询          |
| `findBySymbolAndTradeDate(String symbol, LocalDate tradeDate)`                | 查单日数据                   |

---

## 文件清单

| 文件路径                                                          | 用途                     |
|-------------------------------------------------------------------|--------------------------|
| `db/data/LCO1-伦敦布伦特原油期货历史数据.xlsx`                   | 原始数据源               |
| `db/migration/V2__create_oil_price_daily_ohlcv.sql`               | 建表 DDL                 |
| `db/scripts/import_lco1_ohlcv.py`                                 | Excel → MySQL 导入脚本   |
| `src/main/java/com/citicup/entity/OilPriceDailyOhlcv.java`        | JPA 实体                 |
| `src/main/java/com/citicup/repository/OilPriceDailyOhlcvRepo.java`| Spring Data Repository   |
