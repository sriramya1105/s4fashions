from pydantic import BaseModel, Field
try:
    import email_validator
    from pydantic import EmailStr
except ImportError:
    # Fail-safe email string validation fallback if email-validator package is absent
    EmailStr = str

from typing import Optional, List
from datetime import datetime
from app.models.entities import UserRole, OrderStatus


# ==========================================
# 1. CATEGORY DTOs
# ==========================================
class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    image_url: Optional[str] = Field(None, max_length=500)


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ==========================================
# 2. SUBCATEGORY DTOs
# ==========================================
class SubCategoryCreateRequest(BaseModel):
    category_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2, max_length=60)
    description: Optional[str] = Field(None, max_length=200)


class SubCategoryResponse(BaseModel):
    id: int
    category_id: int
    category_name: Optional[str] = None
    name: str
    slug: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


# ==========================================
# 3. USER & AUTH DTOs
# ==========================================
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    full_name: Optional[str] = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)


class AdminSetupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=64)
    full_name: Optional[str] = Field(None, max_length=100)
    admin_secret: str = Field(..., description="Master admin secret key")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse


# ==========================================
# 4. PRODUCT DTOs
# ==========================================
class ProductCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=180)
    description: str = Field(..., min_length=10, max_length=2000)
    brand: str = Field(..., min_length=2, max_length=60)
    category_id: int = Field(..., gt=0)
    subcategory_id: Optional[int] = Field(None, gt=0)
    available_sizes: str = Field(..., max_length=120)
    available_colors: str = Field(..., max_length=120)
    material: Optional[str] = Field(None, max_length=80)
    price: float = Field(..., gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    stock: int = Field(..., ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    color_images: Optional[str] = Field(None)  # JSON string: {"Black": "https://...", ...}
    specifications: Optional[str] = Field(None)  # Dynamic specs e.g. "Color: Blue, Bottom: Black"


class ProductResponse(BaseModel):
    id: int
    title: str
    description: str
    brand: str
    category_id: int
    category_name: Optional[str] = None
    subcategory_id: Optional[int] = None
    subcategory_name: Optional[str] = None
    available_sizes: str
    available_colors: str
    material: Optional[str]
    price: float
    original_price: Optional[float]
    stock: int
    rating: float
    rating_count: int
    image_url: Optional[str]
    color_images: Optional[str] = None  # JSON string: {"Black": "https://...", ...}
    specifications: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# 5. ORDER DTOs
# ==========================================
class CartItemRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1, max_length=30)
    color: str = Field(..., min_length=1, max_length=50)
    quantity: int = Field(..., gt=0, le=50)


class OrderCheckoutRequest(BaseModel):
    items: List[CartItemRequest] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=10, max_length=300)
    phone_number: str = Field(..., min_length=10, max_length=25, pattern=r"^[0-9+ -]+$")


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_title: str
    size: str
    color: str
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    customer_name: Optional[str] = None  # Populated from User.full_name or User.username
    total_amount: float
    shipping_address: str
    phone_number: str
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
