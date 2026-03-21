package com.citicup.controller;

import com.citicup.entity.Event;
import com.citicup.entity.Exchange;
import com.citicup.service.EventService;
import com.citicup.service.ExchangeService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class DataController {

    private final EventService eventService;
    private final ExchangeService exchangeService;

    public DataController(EventService eventService, ExchangeService exchangeService) {
        this.eventService = eventService;
        this.exchangeService = exchangeService;
    }

    @GetMapping("/api/data/events")
    public Map<String, Object> events() {
        List<Event> eventList = eventService.getEventList();

        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("total", eventList.size());
        data.put("list", eventList);

        result.put("data", data);
        return result;
    }

    @GetMapping("/api/data/exchange")
    public Map<String, Object> exchange() {
        List<Exchange> exchangeList = exchangeService.getExchangeList();

        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("total", exchangeList.size());
        data.put("list", exchangeList);

        result.put("data", data);
        return result;
    }
}