package com.citicup;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class CitiCupApplication {
    public static void main(String[] args) {

        SpringApplication.run(CitiCupApplication.class, args);
    }
}
