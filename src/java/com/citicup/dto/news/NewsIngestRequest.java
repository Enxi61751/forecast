package com.citicup.dto.news;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.time.Instant;

@Data
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