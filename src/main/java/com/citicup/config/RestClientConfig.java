package com.citicup.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestTemplate;

import java.net.InetSocketAddress;
import java.net.Proxy;

@Configuration
public class RestClientConfig {

    /**
     * 代理主机，留空则不走代理。
     * 可在 application.yml 中配置：app.proxy.host / app.proxy.port
     * 也可通过环境变量 APP_PROXY_HOST / APP_PROXY_PORT 注入。
     */
    @Value("${app.proxy.host:}")
    private String proxyHost;

    @Value("${app.proxy.port:7897}")
    private int proxyPort;

    @Bean
    public RestClient restClient() {
        return RestClient.builder().build();
    }

    @Bean
    public RestTemplate restTemplate() {
        if (proxyHost == null || proxyHost.isBlank()) {
            // 未配置代理，直连（内网服务、数据库等不需要代理）
            return new RestTemplate();
        }
        // 配置了代理时，外部 API 请求（如油价 API）通过代理发出
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setProxy(new Proxy(Proxy.Type.HTTP,
                new InetSocketAddress(proxyHost, proxyPort)));
        return new RestTemplate(factory);
    }
}