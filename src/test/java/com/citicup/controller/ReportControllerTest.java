package com.citicup.controller;

import com.citicup.entity.RiskReport;
import com.citicup.service.ReportService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ReportController.class)
class ReportControllerTest {

    @Autowired MockMvc mvc;
    @MockBean ReportService reportService;

    @Test
    void generate_path_returnsReportPayload() throws Exception {
        RiskReport saved = RiskReport.builder()
                .id(99L).predictionRunId(1L).createdAt(Instant.parse("2026-03-21T00:00:00Z"))
                .reportText("body").materialsJson("{}")
                .build();
        when(reportService.generateReport(1L)).thenReturn(saved);

        mvc.perform(post("/api/report/generate/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.id").value(99))
                .andExpect(jsonPath("$.data.predictionRunId").value(1));
    }

    @Test
    void generate_query_get_stripsQuotes() throws Exception {
        RiskReport saved = RiskReport.builder()
                .id(1L).predictionRunId(1L).createdAt(Instant.now())
                .reportText("t").materialsJson("{}")
                .build();
        when(reportService.generateReport(1L)).thenReturn(saved);

        mvc.perform(get("/api/report/generate").param("predictionRunId", "1\""))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.id").value(1));
    }

    @Test
    void generate_predictionRunNotFound_returnsError() throws Exception {
        when(reportService.generateReport(999L))
                .thenThrow(new RuntimeException("predictionRun not found"));

        mvc.perform(post("/api/report/generate/999"))
                .andExpect(status().isInternalServerError())
                .andExpect(jsonPath("$.code").value(-1));
    }
}
