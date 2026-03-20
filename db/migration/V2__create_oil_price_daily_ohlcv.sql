-- Migration V2: 创建 oil_price_daily_ohlcv 表，存储 LCO1 伦敦布伦特原油期货 OHLCV 日线数据
-- 执行时间: 2026-03-20
-- 数据来源: LCO1-伦敦布伦特原油期货历史数据.xlsx（2006-01-03 至 2026-02-20，共 5386 条）

CREATE TABLE IF NOT EXISTS oil_price_daily_ohlcv (
    id          BIGINT       NOT NULL AUTO_INCREMENT PRIMARY KEY,
    symbol      VARCHAR(20)  NOT NULL COMMENT '品种代码，如 LCO1',
    trade_date  DATE         NOT NULL COMMENT '交易日期',
    open_price  DOUBLE       NOT NULL COMMENT '开盘价（美元/桶）',
    close_price DOUBLE       NOT NULL COMMENT '收盘价（美元/桶）',
    high_price  DOUBLE       NOT NULL COMMENT '最高价（美元/桶）',
    low_price   DOUBLE       NOT NULL COMMENT '最低价（美元/桶）',
    volume      VARCHAR(20)           COMMENT '交易量（原始字符串，如 294.58K）',
    change_pct  DOUBLE                COMMENT '涨跌幅（小数形式，如 0.0014 表示 +0.14%）',

    UNIQUE KEY uk_symbol_date (symbol, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='石油期货日线 OHLCV 数据';
