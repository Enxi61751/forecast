package com.citicup.service;

import com.citicup.entity.Exchange;
import com.citicup.repository.ExchangeRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ExchangeService {
    private final ExchangeRepository exchangeRepository;

    public ExchangeService(ExchangeRepository exchangeRepository) {
        this.exchangeRepository = exchangeRepository;
    }

    public List<Exchange> getExchangeList() {
        return exchangeRepository.findAll();
    }
}