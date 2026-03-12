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
    get_all_products
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
    """Get all products"""
    results = get_all_products(limit, offset)
    return {
        "products": results,
        "count": len(results)
    }

# ---------------------------------------------------------
# SEARCH PRODUCTS
# ---------------------------------------------------------
@app.get("/products/search")
def search(q: str, limit: int = 50):
    """Search products by name"""
    results = search_products(q, limit)
    return {
        "products": results,
        "count": len(results)
    }