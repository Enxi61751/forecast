package com.citicup.repository;

import com.citicup.entity.SentimentScore;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SentimentScoreRepo extends JpaRepository<SentimentScore, Long> {}
