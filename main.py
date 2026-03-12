"""
SmartMarket API
FastAPI backend for price comparison
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import (
    get_stats,
    get_categories,
    search_products,
    get_all_products,
    get_product_details,
    get_stores
)

app = FastAPI(
    title="SmartMarket API",
    description="Price comparison across Israeli supermarkets",
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------
@app.get("/")
def root():
    """API info"""
    return {
        "name": "SmartMarket API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "stats": "/stats",
            "categories": "/categories",
            "products": "/products",
            "search": "/products/search?q=query",
            "product_detail": "/products/{barcode}",
            "stores": "/stores"
        }
    }


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------
@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}


# ---------------------------------------------------------
# STATS
# ---------------------------------------------------------
@app.get("/stats")
def stats():
    """Database statistics"""
    return get_stats()


# ---------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------
@app.get("/categories")
def categories():
    """Get all categories with product counts"""
    cats = get_categories()
    
    return {
        "categories": [
            {
                "id": c[0],
                "name": c[1],
                "name_he": c[2],
                "icon": c[3],
                "product_count": c[4]
            }
            for c in cats
        ]
    }


# ---------------------------------------------------------
# PRODUCTS (LIST)
# ---------------------------------------------------------
@app.get("/products")
def products(limit: int = 100, offset: int = 0):
    """Get all products with pagination"""
    rows = get_all_products(limit, offset)
    
    return {
        "products": [
            {
                "barcode": r[0],
                "name": r[1],
                "manufacturer": r[2],
                "category_id": r[3],
                "min_price": float(r[4]) if r[4] else None
            }
            for r in rows
        ],
        "count": len(rows)
    }


# ---------------------------------------------------------
# SEARCH PRODUCTS
# ---------------------------------------------------------
@app.get("/products/search")
def search(q: str, limit: int = 50):
    """Search products by name"""
    rows = search_products(q, limit)
    
    return {
        "products": [
            {
                "barcode": r[0],
                "name": r[1],
                "manufacturer": r[2],
                "category_id": r[3],
                "min_price": float(r[4]) if r[4] else None,
                "stores_count": r[5]
            }
            for r in rows
        ],
        "count": len(rows)
    }


# ---------------------------------------------------------
# PRODUCT DETAILS
# ---------------------------------------------------------
@app.get("/products/{barcode}")
def product_details(barcode: str):
    """Get product details with all prices"""
    result = get_product_details(barcode)
    
    if not result:
        return {"error": "Product not found"}
    
    product = result["product"]
    prices = result["prices"]
    
    return {
        "product": {
            "barcode": product[0],
            "name": product[1],
            "manufacturer": product[2],
            "category_id": product[3]
        },
        "prices": [
            {
                "chain": p[0],
                "store_id": p[1],
                "store_name": p[2],
                "price": float(p[3]) if p[3] else None,
                "updated_at": str(p[4]) if p[4] else None
            }
            for p in prices
        ],
        "best_price": min([float(p[3]) for p in prices if p[3]]) if prices else None
    }


# ---------------------------------------------------------
# STORES
# ---------------------------------------------------------
@app.get("/stores")
def stores():
    """Get all stores"""
    rows = get_stores()
    
    return {
        "stores": [
            {
                "id": r[0],
                "chain": r[1],
                "store_id": r[2],
                "store_name": r[3],
                "city": r[4] if len(r) > 4 else None
            }
            for r in rows
        ]
    }