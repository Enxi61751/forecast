package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;

@Entity
@Table(name = "oil_price_daily_ohlcv",
       uniqueConstraints = @UniqueConstraint(columnNames = {"symbol", "trade_date"}))
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class OilPriceDailyOhlcv {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 品种代码，如 LCO1 */
    @Column(nullable = false, length = 20)
    private String symbol;

    /** 交易日期 */
    @Column(name = "trade_date", nullable = false)
    private LocalDate tradeDate;

    /** 开盘价（美元/桶） */
    @Column(name = "open_price", nullable = false)
    private Double openPrice;

    /** 收盘价（美元/桶） */
    @Column(name = "close_price", nullable = false)
    private Double closePrice;

    /** 最高价（美元/桶） */
    @Column(name = "high_price", nullable = false)
    private Double highPrice;

    /** 最低价（美元/桶） */
    @Column(name = "low_price", nullable = false)
    private Double lowPrice;

    /** 交易量（原始字符串，如 294.58K） */
    @Column(length = 20)
    private String volume;

    /** 涨跌幅（小数，如 0.0014 表示 +0.14%） */
    @Column(name = "change_pct")
    private Double changePct;
}
