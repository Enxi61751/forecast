package com.citicup.repository;

import com.citicup.entity.OilPriceDailyOhlcv;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
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

    @Query("SELECT DISTINCT o.symbol FROM OilPriceDailyOhlcv o ORDER BY o.symbol")
    List<String> findDistinctSymbols();

    @Query("SELECT MIN(o.tradeDate) FROM OilPriceDailyOhlcv o WHERE o.symbol = :symbol")
    Optional<LocalDate> findMinDateBySymbol(@Param("symbol") String symbol);

    @Query("SELECT MAX(o.tradeDate) FROM OilPriceDailyOhlcv o WHERE o.symbol = :symbol")
    Optional<LocalDate> findMaxDateBySymbol(@Param("symbol") String symbol);
}
