from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models.entities import Product, ProductCategory
from app.schemas.dto import ProductResponse

router = APIRouter(prefix="/products", tags=["Product Catalog"])


@router.get(
    "",
    response_model=List[ProductResponse],
    summary="Browse & filter apparel catalog (Men, Women, Kids)"
)
def list_products(
    category: Optional[ProductCategory] = Query(None, description="Filter by Men, Women, or Kids"),
    subcategory: Optional[str] = Query(None, description="e.g. Traditional, Kurtis, Short Tops, Modern"),
    brand: Optional[str] = Query(None, description="Filter by brand, e.g. FabIndia, Biba, Levi's"),
    search: Optional[str] = Query(None, description="Search by keyword in title/description"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """
    Search and filter products using parameterized queries (CWE-89 defense).
    """
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)
    if subcategory:
        query = query.filter(Product.subcategory.ilike(f"%{subcategory}%"))
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        # Parameterized ILIKE search
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.title.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Product.brand.ilike(search_pattern),
            )
        )

    return query.all()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get single product specifications and size/color availability"
)
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    """Retrieve full product details."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found."
        )
    return product
