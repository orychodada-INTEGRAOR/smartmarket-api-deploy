"""
SmartMarket API - Main Application
ה-API הראשי של SmartMarket
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import get_stats, get_categories
from db import test_connection

# ייבוא routers
try:
    from routers.products import router as products_router
    from routers.stores import router as stores_router  
    from routers.compare import router as compare_router
except ImportError:
    import routers_products as products_module
    import routers_stores as stores_module
    import routers_compare as compare_module
    
    products_router = products_module.router
    stores_router = stores_module.router
    compare_router = compare_module.router

# יצירת אפליקציה
app = FastAPI(
    title="SmartMarket API",
    description="API להשוואת מחירים ומוצרים",
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

# חיבור routers
app.include_router(products_router)
app.include_router(stores_router)
app.include_router(compare_router)


@app.get("/", tags=["Root"])
def root():
    """דף הבית"""
    return {
        "name": "SmartMarket API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "products": "/products",
            "search": "/products/search?q=חלב",
            "product_details": "/products/{barcode}",
            "stores": "/stores",
            "compare": "/compare/basket",
            "docs": "/docs",
            "stats": "/stats"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """בדיקת תקינות"""
    db_status = test_connection()
    return {
        "api": "healthy",
        "database": db_status
    }


@app.get("/stats", tags=["Stats"])
def stats():
    """סטטיסטיקות"""
    return get_stats()
@app.get("/categories")@app.get("/categories")
def categories():
    """Get all categories"""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)