"""
SmartMarket API - Stores Router
endpoints לחנויות
"""

from fastapi import APIRouter
from models import get_stores

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get("/")
def list_stores():
    """
    רשימת כל החנויות
    
    מחזיר את כל החנויות במערכת עם מספר המוצרים בכל חנות
    """
    stores = get_stores()
    return {
        "count": len(stores),
        "stores": stores
    }