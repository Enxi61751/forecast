"""
导入 LCO1-伦敦布伦特原油期货历史数据.xlsx 到 MySQL oil_price_daily_ohlcv 表

前置条件:
    pip install openpyxl mysql-connector-python

运行方式（从项目根目录执行）:
    python3 db/scripts/import_lco1_ohlcv.py
"""

import os
import openpyxl
import mysql.connector

DB_CONFIG = {
    "host": "123.206.104.63",
    "port": 3306,
    "user": "citicup_user",
    "password": "citicup123456",
    "database": "citicup",
    "charset": "utf8mb4",
}

XLSX_PATH = os.path.join(os.path.dirname(__file__), "../data/LCO1-伦敦布伦特原油期货历史数据.xlsx")
SYMBOL = "LCO1"

INSERT_SQL = """
    INSERT INTO oil_price_daily_ohlcv
        (symbol, trade_date, open_price, close_price, high_price, low_price, volume, change_pct)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

def main():
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb.active

    # 预读所有行，便于批量插入
    rows_to_insert = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        trade_date, close_price, open_price, high_price, low_price, volume, change_pct = row
        if trade_date is None or close_price is None:
            continue
        if hasattr(trade_date, "date"):
            trade_date = trade_date.date()
        rows_to_insert.append((
            SYMBOL,
            trade_date,
            float(open_price),
            float(close_price),
            float(high_price),
            float(low_price),
            str(volume) if volume is not None else None,
            float(change_pct) if change_pct is not None else None,
        ))

    wb.close()

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    # 分批插入，每批 500 条
    BATCH_SIZE = 500
    for i in range(0, len(rows_to_insert), BATCH_SIZE):
        batch = rows_to_insert[i:i + BATCH_SIZE]
        for record in batch:
            try:
                cursor.execute(INSERT_SQL, record)
                inserted += 1
            except mysql.connector.errors.IntegrityError:
                skipped += 1
        conn.commit()

    cursor.close()
    conn.close()
    print(f"完成：成功导入 {inserted} 条，跳过重复 {skipped} 条。")

if __name__ == "__main__":
    main()
