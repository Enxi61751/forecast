package com.citicup.dto.news;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@Data @Builder @NoArgsConstructor @AllArgsConstructor
public class SentimentResponse {
    private double sentiment;      // 分数
    private double confidence;

    // 极端事件识别（可为空）
    private List<ExtremeEventDto> extremeEvents;

    @Data
    public static class ExtremeEventDto {
        private String eventType;
        private String summary;
        private double intensity;
        private String occurredAt; // ISO 字符串（FastAPI常用）
    }
}
