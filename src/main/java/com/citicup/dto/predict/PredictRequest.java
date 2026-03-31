package com.citicup.dto.predict;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import java.time.Instant;
import java.util.Collections;
import java.util.Map;

@Data
public class PredictRequest {
    @NotBlank
    private String target;     // WTI/Brent
    @NotBlank
    private String horizon;    // 1d/7d/30d

    // 你们可以传：最近N天的指标序列/已聚合特征/或数据源参数
    private Map<String, Object> payload = Collections.emptyMap();

    // 预测基准时间
    private Instant asOf;
}