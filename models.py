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

    # פרטי מוצר
    cur.execute("""
        SELECT barcode, name, manufacturer, category_id
        FROM products
        WHERE barcode = %s
    """, (barcode,))

    product = cur.fetchone()
    if not product:
        conn.close()
        return None

    # מחירים
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

    return {
        "product": product,
        "prices": prices
    }


# ---------------------------------------------------------
# ALL PRODUCTS
# ---------------------------------------------------------
def get_all_products(limit=100, offset=0):
    """קבלת כל המוצרים (עם pagination)"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            p.barcode,
            p.name,
            p.manufacturer,
            p.category_id,
            MIN(pr.price) AS min_price
        FROM products p
        LEFT JOIN prices pr ON p.barcode = pr.product_id
        GROUP BY p.barcode, p.name, p.manufacturer, p.category_id
        ORDER BY p.name
        LIMIT %s OFFSET %s
    """, (limit, offset))

    rows = cur.fetchall()
    conn.close()

    return rows


# ---------------------------------------------------------
# STORES
# ---------------------------------------------------------
def get_stores():
    """קבלת כל החנויות"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            s.id,
            s.chain,
            s.store_id,
            s.store_name,
            COUNT(pr.id) AS products_count
        FROM stores s
        LEFT JOIN prices pr 
            ON s.chain = pr.chain 
            AND s.store_id = pr.store_id
        GROUP BY s.id, s.chain, s.store_id, s.store_name
        ORDER BY s.chain, s.store_id
    """)

    rows = cur.fetchall()
    conn.close()

    return rows


# ---------------------------------------------------------
# COMPARE BASKET
# ---------------------------------------------------------
def compare_basket(products):
    """השוואת סל קניות - מוצא את החנות הזולה ביותר"""
    if not products:
        return {"error": "No products provided"}

    conn = get_connection()
    cur = conn.cursor()

    store_totals = {}
    product_details = []

    for item in products:
        barcode = item.get("barcode")
        quantity = item.get("quantity", 1)

        if not barcode:
            continue

        cur.execute("""
            SELECT 
                pr.chain,
                pr.store_id,
                s.store_name,
                pr.price,
                p.name
            FROM prices pr
            JOIN products p ON pr.product_id = p.barcode
            LEFT JOIN stores s 
                ON pr.chain = s.chain 
                AND pr.store_id = s.store_id
            WHERE pr.product_id = %s
        """, (barcode,))

        prices = cur.fetchall()

        if prices:
            product_prices = []

            for row in prices:
                chain, store_id, store_name, price, name = row
                store_key = f"{chain}_{store_id}"

                if store_key not in store_totals:
                    store_totals[store_key] = {
                        "chain": chain,
                        "store_id": store_id,
                        "store_name": store_name,
                        "total": 0,
                        "items_count": 0
                    }

                price = float(price) if price else 0
                store_totals[store_key]["total"] += price * quantity
                store_totals[store_key]["items_count"] += 1

                product_prices.append({
                    "chain": chain,
                    "store_id": store_id,
                    "price": price
                })

            product_details.append({
                "barcode": barcode,
                "name": prices[0][4],
                "quantity": quantity,
                "prices": product_prices
            })

    conn.close()

    sorted_stores = sorted(store_totals.values(), key=lambda x: x["total"])

    return {
        "products": product_details,
        "stores": sorted_stores,
        "best_store": sorted_stores[0] if sorted_stores else None,
        "savings": (
            sorted_stores[-1]["total"] - sorted_stores[0]["total"]
            if len(sorted_stores) > 1 else 0
        )
    }


# ---------------------------------------------------------
# STATS
# ---------------------------------------------------------
def get_stats():
    """סטטיסטיקות כלליות"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products")
    products_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM stores")
    stores_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM prices")
    prices_count = cur.fetchone()[0]

    conn.close()

    return {
        "products": products_count,
        "stores": stores_count,
        "prices": prices_count
    }


# ---------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------
def get_categories():
    """Get all categories with product counts"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            c.id,
            c.name,
            c.name_he,
            c.icon,
            COUNT(p.id) AS product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id, c.name, c.name_he, c.icon
        ORDER BY c.name_he
    """)

    rows = cur.fetchall()
    conn.close()

    return rows