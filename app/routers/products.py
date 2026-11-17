from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.models.entities import Product, Category, SubCategory
from app.schemas.dto import ProductResponse, CategoryResponse, SubCategoryResponse

router = APIRouter(prefix="", tags=["Public Catalog & Categories"])


# 1. List All Active Categories (Men, Women, Kids)
@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    summary="List all categories for round bubbles navigation"
)
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.is_active == True).order_by(Category.id.asc()).all()


# 2. List Subcategories (Optional filter by category_id or slug)
@router.get(
    "/subcategories",
    response_model=List[SubCategoryResponse],
    summary="List subcategories (e.g. Trousers, Kurtis) filtered by category"
)
def list_subcategories(
    category_id: Optional[int] = Query(None),
    category_slug: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(SubCategory).filter(SubCategory.is_active == True)
    if category_id:
        query = query.filter(SubCategory.category_id == category_id)
    elif category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            query = query.filter(SubCategory.category_id == cat.id)

    results = query.all()
    out = []
    for s in results:
        data = SubCategoryResponse.model_validate(s)
        data.category_name = s.category.name if s.category else None
        out.append(data)
    return out


# 3. Dynamic Products Search & Filter (5-per-row grid)
@router.get(
    "/products",
    response_model=List[ProductResponse],
    summary="Dynamic catalog query with multi-faceted filters"
)
def list_products(
    category_id: Optional[int] = Query(None),
    category_slug: Optional[str] = Query(None),
    subcategory_id: Optional[int] = Query(None),
    subcategory_slug: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == True)

    if category_id:
        query = query.filter(Product.category_id == category_id)
    elif category_slug:
        cat = db.query(Category).filter(Category.slug == category_slug).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)

    if subcategory_id:
        query = query.filter(Product.subcategory_id == subcategory_id)
    elif subcategory_slug:
        sub = db.query(SubCategory).filter(SubCategory.slug == subcategory_slug).first()
        if sub:
            query = query.filter(Product.subcategory_id == sub.id)

    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.title.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Product.brand.ilike(search_pattern)
            )
        )

    products = query.order_by(Product.id.desc()).all()
    
    out = []
    for p in products:
        item = ProductResponse.model_validate(p)
        item.category_name = p.category.name if p.category else None
        item.subcategory_name = p.subcategory.name if p.subcategory else None
        out.append(item)
    return out


# 4. Product Details
@router.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Get single product specifications"
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    item = ProductResponse.model_validate(p)
    item.category_name = p.category.name if p.category else None
    item.subcategory_name = p.subcategory.name if p.subcategory else None
    return item
