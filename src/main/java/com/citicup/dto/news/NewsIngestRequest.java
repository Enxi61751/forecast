package com.citicup.dto.news;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.Instant;

@Data @Builder @NoArgsConstructor @AllArgsConstructor
public class NewsIngestRequest {
    @NotBlank
    private String source;
    @NotBlank
    private String title;
    private String content;
    private String url;

    @NotNull
    private Instant publishedAt;
}
