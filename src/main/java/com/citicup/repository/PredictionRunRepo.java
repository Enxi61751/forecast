package com.citicup.repository;

import com.citicup.entity.NewsArticle;
import org.springframework.data.jpa.repository.JpaRepository;

public interface NewsArticleRepo extends JpaRepository<NewsArticle, Long> {}