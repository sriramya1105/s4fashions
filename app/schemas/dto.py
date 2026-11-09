from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.entities import UserRole, ProductCategory, OrderStatus


# ==========================================
# 1. USER SCHEMAS (Auth & Profile)
# ==========================================
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = UserRole.CUSTOMER  # Default to customer


class UserLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=64)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    full_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse


# ==========================================
# 2. PRODUCT SCHEMAS (Catalog & Inventory)
# ==========================================
class ProductCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=10, max_length=1000)
    brand: str = Field(..., min_length=2, max_length=50)
    category: ProductCategory
    subcategory: str = Field(..., min_length=2, max_length=50)
    available_sizes: str = Field(..., max_length=100)  # e.g. "S,M,L,XL"
    available_colors: str = Field(..., max_length=100)  # e.g. "Navy Blue,Black"
    material: Optional[str] = Field(None, max_length=50)
    price: float = Field(..., gt=0, description="Selling price must be strictly greater than 0")
    original_price: Optional[float] = Field(None, gt=0)
    stock: int = Field(..., ge=0, description="Stock cannot be negative")
    image_url: Optional[str] = Field(None, max_length=255)


class ProductResponse(BaseModel):
    id: int
    title: str
    description: str
    brand: str
    category: ProductCategory
    subcategory: str
    available_sizes: str
    available_colors: str
    material: Optional[str]
    price: float
    original_price: Optional[float]
    stock: int
    rating: float
    rating_count: int
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# 3. ORDER SCHEMAS (Checkout & History)
# ==========================================
class CartItemRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1, max_length=20)
    color: str = Field(..., min_length=1, max_length=50)
    # Defense against quantity manipulation (Negative quantity attack)
    quantity: int = Field(..., gt=0, le=50, description="Quantity must be between 1 and 50")


class OrderCheckoutRequest(BaseModel):
    items: List[CartItemRequest] = Field(..., min_length=1)
    shipping_address: str = Field(..., min_length=10, max_length=300)
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r"^[0-9+ -]+$")


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
    total_amount: float
    shipping_address: str
    phone_number: str
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
