package com.citicup.repository;

import com.citicup.entity.OilPriceDailyOhlcv;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration test: verifies real MySQL connectivity and OilPriceDailyOhlcvRepo queries.
 * Requires the `local` profile (application-local.yml) to reach the database.
 */
@SpringBootTest
@ActiveProfiles("local")
class OilPriceDailyOhlcvRepoTest {

    @Autowired
    OilPriceDailyOhlcvRepo repo;

    // ── 1. Table is not empty ────────────────────────────────────────────────

    @Test
    void table_should_contain_5386_rows() {
        long count = repo.count();
        assertThat(count).isEqualTo(5386L);
    }

    // ── 2. Boundary rows match xlsx source ──────────────────────────────────

    @Test
    void earliest_row_is_2006_01_03() {
        Optional<OilPriceDailyOhlcv> row = repo.findBySymbolAndTradeDate("LCO1", LocalDate.of(2006, 1, 3));
        assertThat(row).isPresent();
        OilPriceDailyOhlcv r = row.get();
        assertThat(r.getSymbol()).isEqualTo("LCO1");
        assertThat(r.getOpenPrice()).isEqualTo(59.35);
        assertThat(r.getClosePrice()).isEqualTo(61.35);
        assertThat(r.getHighPrice()).isEqualTo(62.05);
        assertThat(r.getLowPrice()).isEqualTo(59.08);
        assertThat(r.getVolume()).isEqualTo("70.86K");
    }

    @Test
    void latest_row_is_2026_02_20() {
        Optional<OilPriceDailyOhlcv> row = repo.findBySymbolAndTradeDate("LCO1", LocalDate.of(2026, 2, 20));
        assertThat(row).isPresent();
        OilPriceDailyOhlcv r = row.get();
        assertThat(r.getClosePrice()).isEqualTo(71.76);
        assertThat(r.getChangePct()).isEqualTo(0.0014);
    }

    // ── 3. Date-range query returns correct subset ───────────────────────────

    @Test
    void date_range_query_returns_correct_count() {
        List<OilPriceDailyOhlcv> rows = repo.findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(
                "LCO1",
                LocalDate.of(2006, 1, 3),
                LocalDate.of(2006, 1, 4));
        assertThat(rows).hasSize(2);
        assertThat(rows.get(0).getTradeDate()).isEqualTo(LocalDate.of(2006, 1, 3));
        assertThat(rows.get(1).getTradeDate()).isEqualTo(LocalDate.of(2006, 1, 4));
    }

    // ── 4. OHLC sanity: high >= close >= low for all rows ───────────────────

    @Test
    void ohlc_sanity_high_gte_low_for_all_rows() {
        List<OilPriceDailyOhlcv> all = repo.findBySymbolOrderByTradeDateAsc("LCO1");
        assertThat(all).isNotEmpty();
        for (OilPriceDailyOhlcv r : all) {
            assertThat(r.getHighPrice())
                    .as("high >= low on %s", r.getTradeDate())
                    .isGreaterThanOrEqualTo(r.getLowPrice());
            assertThat(r.getHighPrice())
                    .as("high >= close on %s", r.getTradeDate())
                    .isGreaterThanOrEqualTo(r.getClosePrice());
            assertThat(r.getClosePrice())
                    .as("close >= low on %s", r.getTradeDate())
                    .isGreaterThanOrEqualTo(r.getLowPrice());
        }
    }

    // ── 5. No duplicates (unique key holds) ──────────────────────────────────

    @Test
    void no_duplicate_symbol_date_pairs() {
        List<OilPriceDailyOhlcv> all = repo.findBySymbolOrderByTradeDateAsc("LCO1");
        long distinctDates = all.stream().map(OilPriceDailyOhlcv::getTradeDate).distinct().count();
        assertThat(distinctDates).isEqualTo(all.size());
    }
}
