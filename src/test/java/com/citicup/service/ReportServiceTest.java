package com.citicup.service;

import com.citicup.entity.PredictionRun;
import com.citicup.entity.RiskReport;
import com.citicup.repository.PredictionRunRepo;
import com.citicup.repository.RiskReportRepo;
import com.citicup.service.client.ModelServiceClient;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ReportServiceTest {

    @Mock PredictionRunRepo runRepo;
    @Mock RiskReportRepo reportRepo;
    @Mock ModelServiceClient modelClient;
    @InjectMocks ReportService reportService;

    @Test
    void generateReport_savesReportAndReturnsId() {
        PredictionRun run = PredictionRun.builder()
                .id(1L).target("WTI").horizon("7d")
                .runAt(Instant.now())
                .forecastJson("{\"forecast\":100.0}")
                .extremeClsJson("{\"cls\":0}")
                .build();
        when(runRepo.findById(1L)).thenReturn(Optional.of(run));
        when(reportRepo.findByPredictionRunId(1L)).thenReturn(Optional.empty());
        when(modelClient.simulateAgents(any())).thenReturn("{\"agents\":\"分析结果\"}");
        when(modelClient.generateReport(any())).thenReturn("风险快报正文内容...");

        RiskReport savedReport = RiskReport.builder()
                .id(99L).predictionRunId(1L).createdAt(Instant.now())
                .reportText("风险快报正文内容...").materialsJson("{\"agents\":\"分析结果\"}")
                .build();
        when(reportRepo.save(any())).thenReturn(savedReport);

        RiskReport result = reportService.generateReport(1L);

        assertEquals(99L, result.getId());
        verify(modelClient).simulateAgents(any());
        verify(modelClient).generateReport(any());
        verify(reportRepo).save(any());
    }

    @Test
    void generateReport_updatesWhenReportAlreadyExists() {
        PredictionRun run = PredictionRun.builder()
                .id(1L).target("WTI").horizon("7d")
                .runAt(Instant.now())
                .forecastJson("{}")
                .extremeClsJson("{}")
                .build();
        when(runRepo.findById(1L)).thenReturn(Optional.of(run));
        RiskReport existing = RiskReport.builder()
                .id(42L).predictionRunId(1L).createdAt(Instant.parse("2020-01-01T00:00:00Z"))
                .reportText("old").materialsJson("{}")
                .build();
        when(reportRepo.findByPredictionRunId(1L)).thenReturn(Optional.of(existing));
        when(modelClient.simulateAgents(any())).thenReturn("{\"new\":\"mat\"}");
        when(modelClient.generateReport(any())).thenReturn("new text");
        when(reportRepo.save(any())).thenAnswer(inv -> inv.getArgument(0));

        RiskReport result = reportService.generateReport(1L);

        assertEquals(42L, result.getId());
        assertEquals("new text", result.getReportText());
        assertEquals("{\"new\":\"mat\"}", result.getMaterialsJson());
        verify(reportRepo).save(existing);
    }

    @Test
    void generateReport_predictionRunNotFound_throwsException() {
        when(runRepo.findById(999L)).thenReturn(Optional.empty());

        assertThrows(RuntimeException.class, () -> reportService.generateReport(999L));
        verify(modelClient, never()).simulateAgents(any());
    }

    @Test
    void getLatestReport_returnsReport() {
        RiskReport report = RiskReport.builder()
                .id(1L).predictionRunId(1L).createdAt(Instant.now())
                .reportText("some text").materialsJson("{}").build();
        when(reportRepo.findTopByOrderByPredictionRunIdDesc()).thenReturn(Optional.of(report));

        RiskReport result = reportService.getLatestReport();

        assertNotNull(result);
        assertEquals(1L, result.getId());
    }

    @Test
    void getLatestReport_noReport_throwsException() {
        when(reportRepo.findTopByOrderByPredictionRunIdDesc()).thenReturn(Optional.empty());

        assertThrows(RuntimeException.class, () -> reportService.getLatestReport());
    }
}
