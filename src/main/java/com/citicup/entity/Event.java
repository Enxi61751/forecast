package com.citicup.entity;

import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "events")
public class Event {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;
    private String eventType;

    @Column(columnDefinition = "TEXT")
    private String summary;

    private Double intensity;
    private LocalDateTime occurredAt;
}
