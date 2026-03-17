"""
导入 sentiment_daily_aggregation.csv 到 MySQL 数据库的 indicator_daily 表
"""

import csv
import os
import mysql.connector
from datetime import date

DB_CONFIG = {
    "host": "123.206.104.63",
    "port": 3306,
    "user": "citicup_user",
    "password": "citicup123456",
    "database": "citicup",
    "charset": "utf8mb4",
}

CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/sentiment_daily_aggregation.csv")

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d              = date.fromisoformat(row["date"].strip())
            event_count    = int(row["event_count"])
            pos_count      = int(row["pos_count"])
            neg_count      = int(row["neg_count"])
            sentiment_sum  = float(row["sentiment_sum"])
            sentiment_mean = float(row["sentiment_mean"])
            max_abs        = float(row["max_abs_sentiment"])

            try:
                cursor.execute("""
                    INSERT INTO indicator_daily
                        (date, event_count, pos_count, neg_count,
                         sentiment_sum, sentiment_mean, max_abs_sentiment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (d, event_count, pos_count, neg_count,
                      sentiment_sum, sentiment_mean, max_abs))
                inserted += 1
            except mysql.connector.errors.IntegrityError:
                # 日期唯一键冲突（重复导入时跳过）
                skipped += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"完成：成功导入 {inserted} 条，跳过重复 {skipped} 条。")

if __name__ == "__main__":
    main()
