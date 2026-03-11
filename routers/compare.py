"""
SmartMarket API - Compare Router
השוואת סל קניות
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from models import compare_basket

router = APIRouter(prefix="/compare", tags=["Compare"])


class BasketItem(BaseModel):
    """מוצר בסל"""
    barcode: str
    quantity: int = 1


class BasketRequest(BaseModel):
    """בקשת השוואת סל"""
    products: List[BasketItem]


@router.post("/basket")
def compare_basket_prices(request: BasketRequest):
    """
    השוואת סל קניות - מוצא את החנות הזולה ביותר
    
    שלח רשימת מוצרים ותקבל:
    - החנות הזולה ביותר
    - כל החנויות לפי מחיר
    - חיסכון אפשרי
    
    דוגמה:
    ```json
    {
        "products": [
            {"barcode": "7290000000001", "quantity": 2},
            {"barcode": "7290000000002", "quantity": 1}
        ]
    }
    ```
    """
    if not request.products:
        raise HTTPException(status_code=400, detail="No products provided")
    
    # המרה ל-dict רגיל
    products_list = [
        {"barcode": item.barcode, "quantity": item.quantity}
        for item in request.products
    ]
    
    result = compare_basket(products_list)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result