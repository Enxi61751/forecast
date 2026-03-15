package com.citicup.controller;

import com.citicup.dto.predict.PredictRequest;
import com.citicup.dto.predict.PredictResponse;
import com.citicup.service.PredictService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(PredictController.class)
class PredictControllerTest {

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper objectMapper;
    @MockBean PredictService predictService;

    @Test
    void run_validRequest_returns200WithData() throws Exception {
        PredictRequest req = new PredictRequest();
        req.setTarget("WTI");
        req.setHorizon("1d");
        req.setPayload(Map.of("features", "data"));

        PredictResponse resp = new PredictResponse();
        resp.setForecast("forecastResult");
        resp.setExtremeClass("normal");

        when(predictService.runPrediction(any())).thenReturn(resp);

        mvc.perform(post("/api/predict/run")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.forecast").value("forecastResult"));
    }

    @Test
    void run_missingTarget_returnsValidationError() throws Exception {
        PredictRequest req = new PredictRequest();
        req.setTarget("");        // @NotBlank violation
        req.setHorizon("1d");
        req.setPayload(Map.of("k", "v"));

        mvc.perform(post("/api/predict/run")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(-1));
    }

    @Test
    void run_missingPayload_returnsValidationError() throws Exception {
        PredictRequest req = new PredictRequest();
        req.setTarget("WTI");
        req.setHorizon("1d");
        // payload is null — @NotNull violation

        mvc.perform(post("/api/predict/run")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(-1));
    }
}
