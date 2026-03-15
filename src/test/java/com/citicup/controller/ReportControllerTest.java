package com.citicup.controller;

import com.citicup.service.ReportService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ReportController.class)
class ReportControllerTest {

    @Autowired MockMvc mvc;
    @MockBean ReportService reportService;

    @Test
    void generate_returnsReportId() throws Exception {
        when(reportService.generateReport(1L)).thenReturn(99L);

        mvc.perform(post("/api/report/generate/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data").value(99));
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
