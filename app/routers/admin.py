import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.logging_config import log_admin_event
from app.db.session import get_db
from app.models.entities import Product, Category, SubCategory, Order, OrderItem, User, UserRole, OrderStatus
from app.schemas.dto import (
    ProductCreateRequest, ProductResponse,
    CategoryCreateRequest, CategoryResponse,
    SubCategoryCreateRequest, SubCategoryResponse,
    OrderResponse, AdminSetupRequest, UserResponse
)
from app.core.dependencies import require_admin
from app.core.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin Portal Management"])


def generate_slug(text: str) -> str:
    s = text.lower().strip()
    return re.sub(r'[\s_]+', '-', re.sub(r'[^\w\s-]', '', s))


# ========================================================
# 0. ADMIN ONBOARDING / SETUP (Protected by ADMIN_INVITE_SECRET)
# ========================================================
@router.post("/setup-admin", response_model=UserResponse)
def create_or_promote_admin(
    req: AdminSetupRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Onboard or promote an administrator account using the secure ADMIN_INVITE_SECRET.
    Mitigates unauthorized privilege escalation while allowing legitimate admin creation.
    """
    client_ip = request.client.host if request.client else "unknown"
    if req.admin_secret != settings.ADMIN_INVITE_SECRET:
        log_admin_event(
            "ADMIN_SETUP_REJECTED",
            req.username,
            client_ip,
            "Invalid admin_secret attempted",
            status="BLOCKED",
            level="warning"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Admin Secret Key."
        )

    user = db.query(User).filter(User.username == req.username).first()
    if user:
        user.role = UserRole.ADMIN
        if req.full_name:
            user.full_name = req.full_name
        db.commit()
        db.refresh(user)
        log_admin_event(
            "USER_PROMOTED_TO_ADMIN",
            user.username,
            client_ip,
            f"Existing user '{user.username}' promoted to admin"
        )
        return user

    if not req.email or not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required to create a new admin account."
        )

    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    new_admin = User(
        username=req.username,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        role=UserRole.ADMIN,
        full_name=req.full_name or "Store Administrator"
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    log_admin_event(
        "ADMIN_CREATED",
        new_admin.username,
        client_ip,
        f"New admin '{new_admin.username}' created via admin secret"
    )
    return new_admin


# ========================================================
# 1. CATEGORY MANAGEMENT (Create, List, Delete)
# ========================================================
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def admin_create_category(
    cat_in: CategoryCreateRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    slug = generate_slug(cat_in.name)
    existing = db.query(Category).filter(Category.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Category '{cat_in.name}' already exists.")

    cat = Category(
        name=cat_in.name.strip(),
        slug=slug,
        description=cat_in.description,
        image_url=cat_in.image_url
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/categories", response_model=List[CategoryResponse])
def admin_list_categories(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(Category).order_by(Category.id.asc()).all()


@router.delete("/categories/{cat_id}")
def admin_delete_category(
    cat_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    db.delete(cat)
    db.commit()
    return {"status": "success", "message": f"Category '{cat.name}' deleted."}


# ========================================================
# 2. SUBCATEGORY MANAGEMENT (Connect Trousers -> Men, etc.)
# ========================================================
@router.post("/subcategories", response_model=SubCategoryResponse, status_code=status.HTTP_201_CREATED)
def admin_create_subcategory(
    sub_in: SubCategoryCreateRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    parent_cat = db.query(Category).filter(Category.id == sub_in.category_id).first()
    if not parent_cat:
        raise HTTPException(status_code=404, detail=f"Parent category #{sub_in.category_id} not found.")

    slug = generate_slug(sub_in.name)
    sub = SubCategory(
        category_id=sub_in.category_id,
        name=sub_in.name.strip(),
        slug=slug,
        description=sub_in.description
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    
    resp = SubCategoryResponse.model_validate(sub)
    resp.category_name = parent_cat.name
    return resp


@router.get("/subcategories", response_model=List[SubCategoryResponse])
def admin_list_subcategories(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    results = db.query(SubCategory).order_by(SubCategory.category_id.asc(), SubCategory.id.asc()).all()
    out = []
    for s in results:
        data = SubCategoryResponse.model_validate(s)
        data.category_name = s.category.name if s.category else None
        out.append(data)
    return out


@router.delete("/subcategories/{sub_id}")
def admin_delete_subcategory(
    sub_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    sub = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subcategory not found.")
    db.delete(sub)
    db.commit()
    return {"status": "success", "message": f"Subcategory '{sub.name}' deleted."}


# ========================================================
# 3. DYNAMIC PRODUCT MANAGEMENT (Create, List, Delete)
# ========================================================
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def admin_create_product(
    p_in: ProductCreateRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    cat = db.query(Category).filter(Category.id == p_in.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Selected category does not exist.")

    if p_in.subcategory_id:
        sub = db.query(SubCategory).filter(SubCategory.id == p_in.subcategory_id).first()
        if not sub or sub.category_id != cat.id:
            raise HTTPException(status_code=400, detail="Subcategory does not belong to the selected Category.")

    new_product = Product(
        title=p_in.title.strip(),
        description=p_in.description.strip(),
        brand=p_in.brand.strip(),
        category_id=p_in.category_id,
        subcategory_id=p_in.subcategory_id,
        available_sizes=p_in.available_sizes.strip(),
        available_colors=p_in.available_colors.strip(),
        material=p_in.material.strip() if p_in.material else None,
        price=p_in.price,
        original_price=p_in.original_price or p_in.price,
        stock=p_in.stock,
        image_url=p_in.image_url,
        color_images=p_in.color_images,
        specifications=p_in.specifications
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    res = ProductResponse.model_validate(new_product)
    res.category_name = cat.name
    res.subcategory_name = new_product.subcategory.name if new_product.subcategory else None
    return res


@router.get("/products", response_model=List[ProductResponse])
def admin_list_products(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    products = db.query(Product).order_by(Product.id.desc()).all()
    out = []
    for p in products:
        item = ProductResponse.model_validate(p)
        item.category_name = p.category.name if p.category else None
        item.subcategory_name = p.subcategory.name if p.subcategory else None
        out.append(item)
    return out


@router.delete("/products/{p_id}")
def admin_delete_product(
    p_id: int,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    p = db.query(Product).filter(Product.id == p_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    product_title = p.title
    # Clean up associated order items to avoid foreign key violation
    db.query(OrderItem).filter(OrderItem.product_id == p_id).delete(synchronize_session=False)
    db.delete(p)
    db.commit()

    client_ip = request.client.host if request.client else "unknown"
    log_admin_event("PRODUCT_DELETED", current_admin.username, client_ip, f"Deleted product #{p_id} ('{product_title}')")
    return {"status": "success", "message": f"Product #{p_id} ('{product_title}') deleted successfully."}


# ========================================================
# 4. ORDER FULFILLMENT & STATUS UPDATE
# ========================================================
@router.get("/orders", response_model=List[OrderResponse])
def admin_list_orders(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    out = []
    for order in orders:
        resp = OrderResponse.model_validate(order)
        if order.user:
            resp.customer_name = order.user.full_name or order.user.username
        out.append(resp)
    return out


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def admin_update_order_status(
    order_id: int,
    status_val: OrderStatus,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    order.status = status_val
    db.commit()
    db.refresh(order)
    resp = OrderResponse.model_validate(order)
    if order.user:
        resp.customer_name = order.user.full_name or order.user.username
    return resp


# ========================================================
# 5. DASHBOARD STATS
# ========================================================
@router.get("/stats")
def admin_get_stats(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0.0
    total_orders = db.query(Order).count()
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()

    # Category product distribution for Donut/Pie Chart
    categories = db.query(Category).all()
    cat_distribution = []
    for cat in categories:
        count = db.query(Product).filter(Product.category_id == cat.id).count()
        cat_distribution.append({
            "name": cat.name,
            "count": count
        })

    # Subcategory product breakdown for Bar Chart
    subcategories = db.query(SubCategory).all()
    subcat_distribution = []
    for sub in subcategories:
        count = db.query(Product).filter(Product.subcategory_id == sub.id).count()
        if count > 0:
            subcat_distribution.append({
                "name": sub.name,
                "count": count,
                "category": sub.category.name if sub.category else ""
            })

    # Order status breakdown
    order_statuses = {
        "pending": db.query(Order).filter(Order.status == OrderStatus.PENDING).count(),
        "confirmed": db.query(Order).filter(Order.status == OrderStatus.CONFIRMED).count(),
        "shipped": db.query(Order).filter(Order.status == OrderStatus.SHIPPED).count(),
        "delivered": db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count(),
        "cancelled": db.query(Order).filter(Order.status == OrderStatus.CANCELLED).count(),
    }

    return {
        "status": "success",
        "total_revenue": round(total_sales, 2),
        "total_orders_placed": total_orders,
        "active_catalog_items": total_products,
        "total_categories": total_categories,
        "registered_customers": total_customers,
        "category_distribution": cat_distribution,
        "subcategory_distribution": subcat_distribution,
        "order_statuses": order_statuses
    }
