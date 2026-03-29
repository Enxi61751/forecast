package com.citicup.controller;

import com.citicup.dto.agent.Stage2SingleResponse;
import com.citicup.service.AgentService;
import com.fasterxml.jackson.databind.JsonNode;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AgentController {

    private final AgentService agentService;

    public AgentController(AgentService agentService) {
        this.agentService = agentService;
    }

    @GetMapping("/api/agent/demo/simulate-single")
    public JsonNode simulateSingleDemo() {
        return agentService.simulateSingleDemo();
    }
}