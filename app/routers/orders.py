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
    summary="Place a new clothing order (Strict price & quantity validation)"
)
@limiter.limit(settings.CHECKOUT_RATE_LIMIT)
def checkout_order(
    request: Request,
    order_data: OrderCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates an order for the authenticated customer.
    SECURITY FEATURES:
    1. Quantity and item structure enforced via Pydantic schema (CWE-20).
    2. Unit prices are retrieved strictly from server DB (Prevents client-side price tampering).
    3. Rate limited via SlowAPI (Prevents checkout bot flooding/inventory exhaustion).
    """
    total_amount = 0.0
    order_items_to_create = []

    for item_req in order_data.items:
        # Retrieve product from DB
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

        # Recalculate price server-side
        line_item_total = product.price * item_req.quantity
        total_amount += line_item_total

        # Deduct stock
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

    # Create the Order associated with the currently authenticated user
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


@router.get(
    "",
    response_model=List[OrderResponse],
    summary="List all orders belonging to the authenticated customer"
)
def list_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only the orders placed by the current user.
    Admins may see all or see their own.
    """
    if current_user.role == UserRole.ADMIN:
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
    else:
        orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get single order details with BOLA / IDOR protection (CWE-639)"
)
def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    SECURE OBJECT-LEVEL AUTHORIZATION CHECK (CWE-639 / OWASP API1 Defense):
    Verifies that the order exists AND that either:
    1. The order belongs to the requesting customer (order.user_id == current_user.id)
    2. Or the requester has the 'admin' role.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} was not found."
        )

    # Object-level access control enforcement
    if order.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to view or manage another customer's order."
        )

    return order
