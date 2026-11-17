from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.entities import Product, Order, User, UserRole, OrderStatus
from app.schemas.dto import ProductCreateRequest, ProductResponse, OrderResponse
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


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="[Admin Only] Delete a product from inventory"
)
def admin_delete_product(
    product_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )
    db.delete(product)
    db.commit()
    return {"status": "success", "message": f"Product #{product_id} successfully deleted."}


@router.get(
    "/products",
    response_model=List[ProductResponse],
    summary="[Admin Only] List all inventory items"
)
def admin_list_all_products(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(Product).order_by(Product.id.desc()).all()


@router.get(
    "/orders",
    response_model=List[OrderResponse],
    summary="[Admin Only] List all customer orders across store"
)
def admin_list_all_orders(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
    summary="[Admin Only] Update customer order status (shipped, delivered, etc.)"
)
def admin_update_order_status(
    order_id: int,
    status_val: OrderStatus,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    order.status = status_val
    db.commit()
    db.refresh(order)
    return order


@router.get(
    "/stats",
    summary="[Admin Only] View financial revenue and inventory analytics"
)
def admin_get_analytics(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
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
