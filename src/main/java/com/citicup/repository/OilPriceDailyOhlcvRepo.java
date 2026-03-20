package com.citicup.repository;

import com.citicup.entity.OilPriceDailyOhlcv;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface OilPriceDailyOhlcvRepo extends JpaRepository<OilPriceDailyOhlcv, Long> {

    List<OilPriceDailyOhlcv> findBySymbolOrderByTradeDateAsc(String symbol);

    List<OilPriceDailyOhlcv> findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(
            String symbol, LocalDate start, LocalDate end);

    Optional<OilPriceDailyOhlcv> findBySymbolAndTradeDate(String symbol, LocalDate tradeDate);
}
