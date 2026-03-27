package com.citicup.repository;

import com.citicup.entity.PredictionRun;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface PredictionRunRepo extends JpaRepository<PredictionRun, Long> {

    /** 用于回测时重建历史预测序列，大小写不敏感匹配 target（如 WTI/wti/BRENT/Brent 均可） */
    @Query("SELECT p FROM PredictionRun p WHERE UPPER(p.target) = UPPER(:target) AND p.horizon = :horizon ORDER BY p.runAt ASC")
    List<PredictionRun> findByTargetIgnoreCaseAndHorizonOrderByRunAtAsc(
            @Param("target") String target, @Param("horizon") String horizon);
}
