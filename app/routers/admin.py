from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.entities import Product, Order, User, UserRole
from app.schemas.dto import ProductCreateRequest, ProductResponse
from app.core.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin Portal"])


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin Only] Add a new clothing item to catalog"
)
def admin_add_product(
    product_in: ProductCreateRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Privileged endpoint: Adds new inventory.
    Strictly verifies current_admin has role == 'admin'.
    """
    new_product = Product(
        title=product_in.title,
        description=product_in.description,
        brand=product_in.brand,
        category=product_in.category,
        subcategory=product_in.subcategory,
        available_sizes=product_in.available_sizes,
        available_colors=product_in.available_colors,
        material=product_in.material,
        price=product_in.price,
        original_price=product_in.original_price or product_in.price,
        stock=product_in.stock,
        image_url=product_in.image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get(
    "/stats",
    summary="[Admin Only] View financial revenue and inventory analytics"
)
def admin_get_analytics(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Privileged endpoint: Summarizes platform financials.
    Strictly rejects customers.
    """
    total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0.0
    total_orders = db.query(Order).count()
    total_products = db.query(Product).count()
    total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()

    return {
        "status": "success",
        "total_revenue": round(total_sales, 2),
        "total_orders_placed": total_orders,
        "active_catalog_items": total_products,
        "registered_customers": total_customers
    }
