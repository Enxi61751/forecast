package com.citicup.dto.agent;
public class SessionInfoDto {

    private String phase;
    private int timeToClose;

    public String getPhase() {
        return phase;
    }

    public void setPhase(String phase) {
        this.phase = phase;
    }

    public int getTimeToClose() {
        return timeToClose;
    }

    public void setTimeToClose(int timeToClose) {
        this.timeToClose = timeToClose;
    }
}