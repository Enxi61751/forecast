package com.citicup.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Path;
import java.nio.file.Paths;

@Configuration
public class ExplainabilityStaticResourceConfig implements WebMvcConfigurer {

    @Value("${app.explainability.base-dir:./explainability}")
    private String explainabilityBaseDir;

    @Value("${app.explainability.asset-url-prefix:/explainability-assets}")
    private String assetUrlPrefix;

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        String pattern = assetUrlPrefix.endsWith("/**")
                ? assetUrlPrefix
                : assetUrlPrefix + "/**";

        Path basePath = Paths.get(explainabilityBaseDir).toAbsolutePath().normalize();
        String location = basePath.toUri().toString();

        registry.addResourceHandler(pattern)
                .addResourceLocations(location);
    }
}