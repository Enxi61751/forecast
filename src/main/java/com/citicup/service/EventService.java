package com.citicup.service;

import com.citicup.entity.Event;
import com.citicup.repository.EventRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class EventService {
    private final EventRepository eventRepository;

    public EventService(EventRepository eventRepository) {
        this.eventRepository = eventRepository;
    }

    public List<Event> getEventList() {
        return eventRepository.findAll();
    }
}