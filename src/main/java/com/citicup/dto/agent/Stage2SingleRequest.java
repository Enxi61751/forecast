package com.citicup.dto.agent;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

public class Stage2SingleRequest {

    @JsonProperty("input")
    private SimulationInputDto simulationInput;

    private double currentPrice;
    private double currentVolatility;
    private int dealerInventory;
    private int maxPositionLimit = 500;
    private int seed = 7;
    private ClearingParametersDto clearingParameters;
    private List<ClearingCalibrationObservationDto> calibrationObservations;
    private String calibrationFile;
    private Map<String, SelfStateDto> agentStates;
    private ExecutionStateDto executionState;

    public SimulationInputDto getSimulationInput() {
        return simulationInput;
    }

    public void setSimulationInput(SimulationInputDto simulationInput) {
        this.simulationInput = simulationInput;
    }

    public double getCurrentPrice() {
        return currentPrice;
    }

    public void setCurrentPrice(double currentPrice) {
        this.currentPrice = currentPrice;
    }

    public double getCurrentVolatility() {
        return currentVolatility;
    }

    public void setCurrentVolatility(double currentVolatility) {
        this.currentVolatility = currentVolatility;
    }

    public int getDealerInventory() {
        return dealerInventory;
    }

    public void setDealerInventory(int dealerInventory) {
        this.dealerInventory = dealerInventory;
    }

    public int getMaxPositionLimit() {
        return maxPositionLimit;
    }

    public void setMaxPositionLimit(int maxPositionLimit) {
        this.maxPositionLimit = maxPositionLimit;
    }

    public int getSeed() {
        return seed;
    }

    public void setSeed(int seed) {
        this.seed = seed;
    }

    public ClearingParametersDto getClearingParameters() {
        return clearingParameters;
    }

    public void setClearingParameters(ClearingParametersDto clearingParameters) {
        this.clearingParameters = clearingParameters;
    }

    public List<ClearingCalibrationObservationDto> getCalibrationObservations() {
        return calibrationObservations;
    }

    public void setCalibrationObservations(List<ClearingCalibrationObservationDto> calibrationObservations) {
        this.calibrationObservations = calibrationObservations;
    }

    public String getCalibrationFile() {
        return calibrationFile;
    }

    public void setCalibrationFile(String calibrationFile) {
        this.calibrationFile = calibrationFile;
    }

    public Map<String, SelfStateDto> getAgentStates() {
        return agentStates;
    }

    public void setAgentStates(Map<String, SelfStateDto> agentStates) {
        this.agentStates = agentStates;
    }

    public ExecutionStateDto getExecutionState() {
        return executionState;
    }

    public void setExecutionState(ExecutionStateDto executionState) {
        this.executionState = executionState;
    }
}