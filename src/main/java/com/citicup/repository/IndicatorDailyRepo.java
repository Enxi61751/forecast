package com.citicup.repository;

import com.citicup.entity.IndicatorDaily;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface IndicatorDailyRepo extends JpaRepository<IndicatorDaily, Long> {
    List<IndicatorDaily> findAllByOrderByDateAsc();
}