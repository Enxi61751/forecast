package com.citicup.entity;

import jakarta.persistence.*;

import java.time.LocalDate;

@Entity
@Table(name = "exchange")
public class Exchange {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private LocalDate date;
    private Double rate;
}
