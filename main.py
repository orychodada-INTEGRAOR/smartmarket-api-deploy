"""
SmartMarket API
FastAPI backend for price comparison
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import get_stats, get_categories

app = FastAPI(
    title="SmartMarket API",
    description="Price comparison across Israeli supermarkets",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}

@app.get("/stats")
def stats():
    """Database statistics"""
    return get_stats()

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