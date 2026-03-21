-- Initialize test data for CitiCup application
-- This script uses UNIX_TIMESTAMP for time calculations to be compatible with different MySQL versions

-- 1. Insert test data into news table (Summary field required)
INSERT INTO `news` (`title`, `source`, `summary`, `url`, `published_at`, `sentiment_label`, `sentiment_score`) VALUES
('全球油价持续上升', 'Reuters', '受OPEC+减产影响，WTI原油价格跟随上升走势', 'https://example.com/news1', DATE_SUB(NOW(), INTERVAL 1 DAY), 'positive', 0.75),
('美元指数承压', 'Bloomberg', '美联储政策转向鸽派，美元开始回落', 'https://example.com/news2', DATE_SUB(NOW(), INTERVAL 12 HOUR), 'neutral', 0.62),
('中东局势升温', 'CNBC', '地缘政治风险推动能源价格上涨', 'https://example.com/news3', DATE_SUB(NOW(), INTERVAL 6 HOUR), 'negative', 0.45);

-- 2. Insert test data into exchange table
INSERT INTO `exchange` (`date`, `rate`) VALUES
(DATE_SUB(CURDATE(), INTERVAL 5 DAY), 7.18),
(DATE_SUB(CURDATE(), INTERVAL 4 DAY), 7.19),
(DATE_SUB(CURDATE(), INTERVAL 3 DAY), 7.21),
(DATE_SUB(CURDATE(), INTERVAL 2 DAY), 7.20),
(DATE_SUB(CURDATE(), INTERVAL 1 DAY), 7.22),
(CURDATE(), 7.23);

-- 3. Insert test data into news_article table
INSERT INTO `news_article` (`source`, `title`, `content`, `url`, `published_at`, `ingested_at`) VALUES
('Reuters', '油价创年内新高', '受多项因素影响，油价创年内新高水平', 'https://example.com/article1', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
('Bloomberg', 'OPEC+ 决定维持减产', 'OPEC+ 在紧急会议中决定继续维持减产计划', 'https://example.com/article2', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
('CNBC', '美国库存数据显示需求强劲', '美国原油库存意外下降，显示需求恢复良好', 'https://example.com/article3', NOW(), NOW());

-- 4. Insert test data into oil_price_history table
INSERT INTO `oil_price_history` (`type`, `price`, `currency`, `unit`, `change_percent`, `timestamp`) VALUES
('WTI', 76.50, 'USD', 'barrel', '+1.2%', DATE_SUB(NOW(), INTERVAL 7 DAY)),
('WTI', 75.80, 'USD', 'barrel', '-0.9%', DATE_SUB(NOW(), INTERVAL 6 DAY)),
('WTI', 77.20, 'USD', 'barrel', '+1.8%', DATE_SUB(NOW(), INTERVAL 5 DAY)),
('WTI', 78.10, 'USD', 'barrel', '+1.2%', DATE_SUB(NOW(), INTERVAL 4 DAY)),
('WTI', 77.50, 'USD', 'barrel', '-0.8%', DATE_SUB(NOW(), INTERVAL 3 DAY)),
('WTI', 78.90, 'USD', 'barrel', '+1.8%', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('WTI', 79.50, 'USD', 'barrel', '+0.8%', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('WTI', 80.25, 'USD', 'barrel', '+0.9%', NOW()),
('BRENT', 81.10, 'USD', 'barrel', '+1.1%', DATE_SUB(NOW(), INTERVAL 7 DAY)),
('BRENT', 80.40, 'USD', 'barrel', '-0.9%', DATE_SUB(NOW(), INTERVAL 6 DAY)),
('BRENT', 81.80, 'USD', 'barrel', '+1.7%', DATE_SUB(NOW(), INTERVAL 5 DAY)),
('BRENT', 82.70, 'USD', 'barrel', '+1.1%', DATE_SUB(NOW(), INTERVAL 4 DAY)),
('BRENT', 81.90, 'USD', 'barrel', '-1.0%', DATE_SUB(NOW(), INTERVAL 3 DAY)),
('BRENT', 83.30, 'USD', 'barrel', '+1.7%', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('BRENT', 83.95, 'USD', 'barrel', '+0.8%', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('BRENT', 84.70, 'USD', 'barrel', '+0.9%', NOW());

-- 5. Insert test data into prediction_run table
INSERT INTO `prediction_run` (`target`, `horizon`, `run_at`, `forecast_json`, `extreme_cls_json`) VALUES
('WTI', '7d', DATE_SUB(NOW(), INTERVAL 2 DAY), 
 '{"predictions":[{"date":"2026-03-28","value":81.2},{"date":"2026-03-29","value":81.8},{"date":"2026-03-30","value":82.3},{"date":"2026-03-31","value":81.9}]}',
 '{"class":"normal","confidence":0.92,"risk_level":"medium"}'),
('WTI', '30d', DATE_SUB(NOW(), INTERVAL 1 DAY),
 '{"predictions":[{"date":"2026-04-15","value":79.5},{"date":"2026-04-20","value":80.2},{"date":"2026-04-30","value":78.9}]}',
 '{"class":"normal","confidence":0.88,"risk_level":"medium"}'),
('BRENT', '7d', NOW(),
 '{"predictions":[{"date":"2026-03-28","value":85.6},{"date":"2026-03-29","value":86.2},{"date":"2026-03-30","value":86.8},{"date":"2026-03-31","value":86.1}]}',
 '{"class":"normal","confidence":0.90,"risk_level":"medium"}');

-- 6. Insert test data into risk_report table
INSERT INTO `risk_report` (`prediction_run_id`, `created_at`, `report_text`, `materials_json`) VALUES
(1, DATE_SUB(NOW(), INTERVAL 1 DAY), 
 '【油价风险快报】\n分析时间：2026-03-21\n标的：WTI\n期限：7d\n\n【预测结论】\n基于多源数据分析，预测WTI油价在未来7天内保持上升趋势。\n\n【风险提示】\n1. 地缘政治风险可能导致油价快速上涨\n2. 美元升值可能压制油价\n3. 全球经济衰退风险需关注',
 '{"agents":[{"agent":"fundamental_analysis","conclusion":"Oil fundamentals remain supportive"},{"agent":"technical_analysis","conclusion":"Uptrend remains intact"}]}');

-- 7. Insert test sentiment scores for news articles
INSERT INTO `sentiment_score` (`news_id`, `sentiment`, `confidence`, `scored_at`) VALUES
(1, 0.75, 0.88, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(2, 0.62, 0.85, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(3, 0.80, 0.91, NOW());

-- 8. Insert test extreme events
INSERT INTO `extreme_event` (`news_id`, `event_type`, `summary`, `intensity`, `occurred_at`, `created_at`) VALUES
(1, 'price_surge', 'Oil price spike due to supply constraints', 0.85, DATE_SUB(NOW(), INTERVAL 2 DAY), NOW()),
(2, 'geopolitical', 'Middle East tension affecting market', 0.78, DATE_SUB(NOW(), INTERVAL 1 DAY), NOW());
