"""
导入 event_detail.csv 到 MySQL 数据库
每行 CSV 数据拆分写入三张表：news_article、extreme_event、sentiment_score
"""

import csv
import os
import mysql.connector
from datetime import datetime, timezone

DB_CONFIG = {
    "host": "123.206.104.63",
    "port": 3306,
    "user": "citicup_user",
    "password": "citicup123456",
    "database": "citicup",
    "charset": "utf8mb4",
}

CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/event_detail.csv")

def parse_dt(s):
    """把 CSV 里的时间字符串转成 datetime（UTC）"""
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    inserted = 0
    skipped = 0

    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event_time   = parse_dt(row["event_time"])
            event_type   = row["event_type"].strip()
            direction    = float(row["sentiment_direction"])
            intensity    = float(row["sentiment_intensity"])
            signed_score = round(direction * abs(intensity), 6)   # 带符号的情绪分
            title        = row["title"].strip()
            summary      = row["summary"].strip()
            source       = row["source"].strip()
            url          = row["url"].strip()

            # ── 1. 写 news_article ────────────────────────────────────
            cursor.execute("""
                INSERT INTO news_article (source, title, content, url, published_at, ingested_at)
                VALUES (%s, %s, NULL, %s, %s, %s)
            """, (source, title, url, event_time, now))
            news_id = cursor.lastrowid

            # ── 2. 写 extreme_event ───────────────────────────────────
            cursor.execute("""
                INSERT INTO extreme_event (news_id, event_type, summary, intensity, occurred_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (news_id, event_type, summary, signed_score, event_time, now))

            # ── 3. 写 sentiment_score ─────────────────────────────────
            cursor.execute("""
                INSERT INTO sentiment_score (news_id, sentiment, confidence, scored_at)
                VALUES (%s, %s, NULL, %s)
            """, (news_id, signed_score, event_time))

            inserted += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"完成：成功导入 {inserted} 条事件，跳过 {skipped} 条。")

if __name__ == "__main__":
    main()
