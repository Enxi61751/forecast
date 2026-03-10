package com.citicup.repository;

import com.citicup.entity.OilPriceHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface OilPriceHistoryRepo extends JpaRepository<OilPriceHistory, Long> {

    List<OilPriceHistory> findByTimestampBetween(LocalDateTime start, LocalDateTime end);

}
