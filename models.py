"""
SmartMarket API - Models
שאילתות SQL ולוגיקה עסקית
"""

from db import get_connection


# ---------------------------------------------------------
# SEARCH PRODUCTS
# ---------------------------------------------------------
def search_products(query, limit=50):
    """חיפוש מוצרים לפי שם"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            p.barcode,
            p.name,
            p.manufacturer,
            p.category_id,
            MIN(pr.price) AS min_price,
            COUNT(pr.id) AS stores_count
        FROM products p
        LEFT JOIN prices pr ON p.barcode = pr.product_id
        WHERE p.name ILIKE %s
        GROUP BY p.barcode, p.name, p.manufacturer, p.category_id
        ORDER BY p.name
        LIMIT %s
    """, (f"%{query}%", limit))

    rows = cur.fetchall()
    conn.close()

    return rows


# ---------------------------------------------------------
# PRODUCT DETAILS
# ---------------------------------------------------------
def get_product_details(barcode):
    """קבלת פרטי מוצר מלאים + מחירים מכל החנויות"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT barcode, name, manufacturer, category_id
        FROM products
        WHERE barcode = %s
    """, (barcode,))
    product = cur.fetchone()

    if not product:
        conn.close()
        return None

    cur.execute("""
        SELECT 
            pr.chain,
            pr.store_id,
            s.store_name,
            pr.price,
            pr.updated_at
        FROM prices pr
        LEFT JOIN stores s 
            ON pr.chain = s.chain 
            AND pr.store_id = s.store_id
        WHERE pr.product_id = %s
        ORDER BY pr.price ASC
    """, (barcode,))
    prices = cur.fetchall()

    conn.close()