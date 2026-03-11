"""
SmartMarket API - Products Router
endpoints למוצרים
"""

from fastapi import APIRouter, Query, HTTPException
from models import search_products, get_product_details, get_all_products

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
def list_products(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    רשימת מוצרים (עם pagination)
    
    - **limit**: מספר מוצרים לדף (1-1000)
    - **offset**: היסט לדפדוף
    """
    products = get_all_products(limit=limit, offset=offset)
    return {
        "count": len(products),
        "limit": limit,
        "offset": offset,
        "products": products
    }


@router.get("/search")
def search(
    q: str = Query(..., min_length=1, description="מילת חיפוש"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    חיפוש מוצרים
    
    - **q**: מילת חיפוש (חובה)
    - **limit**: מספר תוצאות מקסימלי
    
    דוגמה: /products/search?q=חלב
    """
    results = search_products(query=q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }


@router.get("/{barcode}")
def get_product(barcode: str):
    """
    פרטי מוצר מלאים + מחירים מכל החנויות
    
    - **barcode**: ברקוד המוצר
    
    דוגמה: /products/7290000000001
    """
    product = get_product_details(barcode)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product