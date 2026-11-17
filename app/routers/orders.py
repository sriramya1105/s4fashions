from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.models.entities import Order, OrderItem, Product, User, UserRole, OrderStatus
from app.schemas.dto import OrderCheckoutRequest, OrderResponse
from app.core.dependencies import get_current_user
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/orders", tags=["Orders & Checkout"])


@router.post(
    "/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place order with strict server-side price calculation"
)
@limiter.limit(settings.CHECKOUT_RATE_LIMIT)
def checkout_order(
    request: Request,
    order_data: OrderCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    total_amount = 0.0
    order_items_to_create = []

    for item_req in order_data.items:
        product = db.query(Product).filter(Product.id == item_req.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product ID {item_req.product_id} does not exist."
            )

        if product.stock < item_req.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient inventory stock for '{product.title}'. Only {product.stock} available."
            )

        # Recalculate price server-side (prevents client price tampering)
        line_item_total = product.price * item_req.quantity
        total_amount += line_item_total
        product.stock -= item_req.quantity

        order_item = OrderItem(
            product_id=product.id,
            product_title=product.title,
            size=item_req.size,
            color=item_req.color,
            quantity=item_req.quantity,
            unit_price=product.price,
        )
        order_items_to_create.append(order_item)

    new_order = Order(
        user_id=current_user.id,
        total_amount=round(total_amount, 2),
        shipping_address=order_data.shipping_address,
        phone_number=order_data.phone_number,
        status=OrderStatus.CONFIRMED,
        items=order_items_to_create
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("", response_model=List[OrderResponse])
def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.ADMIN:
        return db.query(Order).order_by(Order.created_at.desc()).all()
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # BOLA / IDOR Protection (CWE-639)
    if order.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot view another customer's order."
        )
    return order
