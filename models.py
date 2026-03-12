"""
SmartMarket API - Models
שאילתות SQL ולוגיקה עסקית
"""

from db import get_connection


def search_products(query, limit=50):
    """
    חיפוש מוצרים לפי שם
    
    Args:
        query: מילת חיפוש
        limit: מספר תוצאות מקסימלי
        
    Returns:
        רשימת מוצרים
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT DISTINCT ON (p.barcode)
            p.barcode,
            p.name,
            p.manufacturer,
            p.category,
            MIN(pr.price) as min_price,
            MAX(pr.price) as max_price,
            COUNT(pr.id) as stores_count
        FROM products p
        LEFT JOIN prices pr ON p.barcode = pr.product_id
        WHERE p.name ILIKE %s
        GROUP BY p.barcode, p.name, p.manufacturer, p.category
        ORDER BY p.barcode, p.name
        LIMIT %s
    """, (f"%{query}%", limit))
    
    rows = cur.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_product_details(barcode):
    """
    קבלת פרטי מוצר מלאים + מחירים מכל החנויות
    
    Args:
        barcode: ברקוד המוצר
        
    Returns:
        dict עם פרטי מוצר ומחירים
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # פרטי מוצר
    cur.execute("""
        SELECT barcode, name, manufacturer, category
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
        LEFT JOIN stores s ON pr.chain = s.chain AND pr.store_id = s.store_id
        WHERE pr.product_id = %s
        ORDER BY pr.price ASC
    """, (barcode,))
    
    prices = cur.fetchall()
    conn.close()
    
    return {
        "product": dict(product),
        "prices": [dict(p) for p in prices]
    }


def get_all_products(limit=100, offset=0):
    """
    קבלת כל המוצרים (עם pagination)
    
    Args:
        limit: מספר מוצרים לדף
        offset: היסט (לדפדוף)
        
    Returns:
        רשימת מוצרים
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            p.barcode,
            p.name,
            p.manufacturer,
            p.category,
            MIN(pr.price) as min_price
        FROM products p
        LEFT JOIN prices pr ON p.barcode = pr.product_id
        GROUP BY p.barcode, p.name, p.manufacturer, p.category
        ORDER BY p.name
        LIMIT %s OFFSET %s
    """, (limit, offset))
    
    rows = cur.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_stores():
    """
    קבלת כל החנויות
    
    Returns:
        רשימת חנויות
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            s.id,
            s.chain,
            s.store_id,
            s.store_name,
            COUNT(pr.id) as products_count
        FROM stores s
        LEFT JOIN prices pr ON s.chain = pr.chain AND s.store_id = pr.store_id
        GROUP BY s.id, s.chain, s.store_id, s.store_name
        ORDER BY s.chain, s.store_id
    """)
    
    rows = cur.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def compare_basket(products):
    """
    השוואת סל קניות - מוצא את החנות הזולה ביותר
    
    Args:
        products: רשימת מוצרים [{"barcode": "123", "quantity": 2}, ...]
        
    Returns:
        dict עם תוצאות השוואה
    """
    if not products:
        return {"error": "No products provided"}
    
    conn = get_connection()
    cur = conn.cursor()
    
    # מבנה לאחסון סכומים לפי חנות
    store_totals = {}
    product_details = []
    
    for item in products:
        barcode = item.get("barcode")
        quantity = item.get("quantity", 1)
        
        if not barcode:
            continue
        
        # קבל מחירים לכל חנות
        cur.execute("""
            SELECT 
                pr.chain,
                pr.store_id,
                s.store_name,
                pr.price,
                p.name
            FROM prices pr
            JOIN products p ON pr.product_id = p.barcode
            LEFT JOIN stores s ON pr.chain = s.chain AND pr.store_id = s.store_id
            WHERE pr.product_id = %s
        """, (barcode,))
        
        prices = cur.fetchall()
        
        if prices:
            product_prices = []
            for price_row in prices:
                store_key = f"{price_row['chain']}_{price_row['store_id']}"
                price = float(price_row['price']) if price_row['price'] else 0
                
                # צבור סכום לחנות
                if store_key not in store_totals:
                    store_totals[store_key] = {
                        'chain': price_row['chain'],
                        'store_id': price_row['store_id'],
                        'store_name': price_row['store_name'],
                        'total': 0,
                        'items_count': 0
                    }
                
                store_totals[store_key]['total'] += price * quantity
                store_totals[store_key]['items_count'] += 1
                
                product_prices.append({
                    'chain': price_row['chain'],
                    'store_id': price_row['store_id'],
                    'price': price
                })
            
            product_details.append({
                'barcode': barcode,
                'name': prices[0]['name'],
                'quantity': quantity,
                'prices': product_prices
            })
    
    conn.close()
    
    # מיין לפי מחיר
    sorted_stores = sorted(
        store_totals.values(),
        key=lambda x: x['total']
    )
    
    result = {
        'products': product_details,
        'stores': sorted_stores,
        'best_store': sorted_stores[0] if sorted_stores else None,
        'savings': sorted_stores[-1]['total'] - sorted_stores[0]['total'] if len(sorted_stores) > 1 else 0
    }
    
    return result


def get_stats():
    """
    סטטיסטיקות כלליות
    
    Returns:
        dict עם מספרים
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # מוצרים
    cur.execute("SELECT COUNT(*) as count FROM products")
    products_count = cur.fetchone()['count']
    
    # חנויות
    cur.execute("SELECT COUNT(*) as count FROM stores")
    stores_count = cur.fetchone()['count']
    
    # מחירים
    cur.execute("SELECT COUNT(*) as count FROM prices")
    prices_count = cur.fetchone()['count']
    
    conn.close()
    
    return {
        'products': products_count,
        'stores': stores_count,
        'prices': prices_count
    }
def get_categories():
    """Get all categories with product counts"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT c.id, c.name, c.name_he, c.icon,
               COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id, c.name, c.name_he, c.icon
        ORDER BY c.name_he
    """)
    
    categories = cur.fetchall()
    cur.close()
    conn.close()
    
    return categories