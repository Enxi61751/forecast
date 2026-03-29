package com.citicup.dto.agent;
import java.util.ArrayList;
import java.util.List;

public class ExecutionStateDto {

    private List<StandardOrderDto> workingOrders = new ArrayList<>();
    private int nextOrderSequence = 1;

    public List<StandardOrderDto> getWorkingOrders() {
        return workingOrders;
    }

    public void setWorkingOrders(List<StandardOrderDto> workingOrders) {
        this.workingOrders = workingOrders;
    }

    public int getNextOrderSequence() {
        return nextOrderSequence;
    }

    public void setNextOrderSequence(int nextOrderSequence) {
        this.nextOrderSequence = nextOrderSequence;
    }
}