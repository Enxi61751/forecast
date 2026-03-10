package com.citicup.repository;

import com.citicup.entity.ExtremeEvent;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ExtremeEventRepo extends JpaRepository<ExtremeEvent, Long> {}