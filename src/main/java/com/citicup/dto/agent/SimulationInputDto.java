package com.citicup.dto.agent;

import com.fasterxml.jackson.annotation.JsonProperty;

public class SimulationInputDto {

    private EnvironmentDto environment;
    private EventDto event;

    @JsonProperty("self")
    private SelfStateDto selfState;

    public EnvironmentDto getEnvironment() {
        return environment;
    }

    public void setEnvironment(EnvironmentDto environment) {
        this.environment = environment;
    }

    public EventDto getEvent() {
        return event;
    }

    public void setEvent(EventDto event) {
        this.event = event;
    }

    public SelfStateDto getSelfState() {
        return selfState;
    }

    public void setSelfState(SelfStateDto selfState) {
        this.selfState = selfState;
    }
}