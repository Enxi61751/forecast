package com.citicup.repository;

import com.citicup.entity.RiskReport;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;


public interface RiskReportRepo extends JpaRepository<RiskReport, Long> {

    // 获取 predictionRunId 最大的那条报告
    Optional<RiskReport> findTopByOrderByPredictionRunIdDesc();

}
