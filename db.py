"""
SmartMarket API - Database Connection
חיבור ל-PostgreSQL
"""

import os
import psycopg2


def get_connection():
    """
    מחזיר חיבור ל-PostgreSQL
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "switchback.proxy.rlwy.net"),
        port=int(os.getenv("DB_PORT", "45220")),
        database=os.getenv("DB_NAME", "railway"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "hNRPqAkvvnxRCrCEzJwnhZqExaxlCYcJ")
    )


def test_connection():
    """
    בדיקת חיבור ל-DB
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products")
        result = cur.fetchone()
        conn.close()
        return {"status": "connected", "products": result[0]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    result = test_connection()
    print(result)