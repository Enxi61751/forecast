package com.citicup.service;

import com.citicup.dto.explainability.ExplainabilityModelOptionDto;
import com.citicup.dto.explainability.ExplainabilityRecordDto;
import com.citicup.dto.explainability.ExplainabilityResponseDto;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.stream.Stream;

@Service
@RequiredArgsConstructor
public class ExplainabilityService {

    private final ObjectMapper objectMapper;

    @Value("${app.explainability.base-dir:./explainability}")
    private String baseDir;

    @Value("${app.explainability.asset-url-prefix:/explainability-assets}")
    private String assetUrlPrefix;

    public List<ExplainabilityModelOptionDto> listModels() {
        Path root = getBaseDirPath();
        if (!Files.exists(root) || !Files.isDirectory(root)) {
            return List.of();
        }

        List<ExplainabilityModelOptionDto> result = new ArrayList<>();

        try (Stream<Path> stream = Files.list(root)) {
            stream.filter(Files::isDirectory)
                    .sorted(Comparator.comparing(path -> path.getFileName().toString()))
                    .forEach(modelDir -> {
                        String modelKey = modelDir.getFileName().toString();
                        Path resultsJson = modelDir.resolve("results.json");
                        if (!Files.exists(resultsJson)) {
                            return;
                        }

                        String label = modelKey;
                        try {
                            ExplainabilityResponseDto dto = readModelResults(modelKey);
                            if (dto.getOverview() != null && dto.getOverview().getModelName() != null) {
                                label = dto.getOverview().getModelName();
                            }
                        } catch (Exception ignored) {
                        }

                        result.add(new ExplainabilityModelOptionDto(modelKey, label));
                    });
        } catch (IOException e) {
            throw new RuntimeException("Failed to scan explainability model list: " + e.getMessage(), e);
        }

        return result;
    }

    public ExplainabilityResponseDto getByModelKey(String modelKey) {
        return readModelResults(modelKey);
    }

    public ExplainabilityRecordDto getRecord(String modelKey, String trainDate) {
        ExplainabilityResponseDto dto = readModelResults(modelKey);
        return dto.getRecords().stream()
                .filter(record -> trainDate.equals(record.getTrainDate()))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException(
                        "Explainability record not found for model=" + modelKey + ", trainDate=" + trainDate
                ));
    }

    private ExplainabilityResponseDto readModelResults(String modelKey) {
        Path modelDir = getBaseDirPath().resolve(modelKey).normalize();
        Path resultsJson = modelDir.resolve("results.json");

        if (!Files.exists(resultsJson)) {
            throw new IllegalArgumentException("Explainability results.json not found for model: " + modelKey);
        }

        try {
            ExplainabilityResponseDto dto = objectMapper.readValue(resultsJson.toFile(), ExplainabilityResponseDto.class);
            normalizePaths(modelKey, dto);
            return dto;
        } catch (IOException e) {
            throw new RuntimeException("Failed to read explainability results for model " + modelKey + ": " + e.getMessage(), e);
        }
    }

    private void normalizePaths(String modelKey, ExplainabilityResponseDto dto) {
        if (dto == null || dto.getRecords() == null) {
            return;
        }

        for (ExplainabilityRecordDto record : dto.getRecords()) {
            record.setSummaryPlot(normalizeAssetPath(modelKey, record.getSummaryPlot()));
            record.setBarPlot(normalizeAssetPath(modelKey, record.getBarPlot()));
        }
    }

    private String normalizeAssetPath(String modelKey, String rawPath) {
        if (rawPath == null || rawPath.isBlank()) {
            return rawPath;
        }

        String normalized = rawPath.replace("\\", "/");

        String lower = normalized.toLowerCase(Locale.ROOT);
        if (lower.startsWith("http://") || lower.startsWith("https://") || normalized.startsWith("/")) {
            return normalized;
        }

        String prefix = assetUrlPrefix.endsWith("/") ? assetUrlPrefix.substring(0, assetUrlPrefix.length() - 1) : assetUrlPrefix;
        return prefix + "/" + modelKey + "/" + normalized;
    }

    private Path getBaseDirPath() {
        return Paths.get(baseDir).toAbsolutePath().normalize();
    }
}