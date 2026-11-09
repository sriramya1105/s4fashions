from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class ProductCategory(str, enum.Enum):
    MEN = "men"
    WOMEN = "women"
    KIDS = "kids"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    full_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=False)
    brand = Column(String(50), nullable=False, index=True)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    subcategory = Column(String(50), nullable=False, index=True)
    # Available sizes stored as comma-separated or JSON string, e.g. "S,M,L,XL"
    available_sizes = Column(String(100), nullable=False, default="S,M,L,XL")
    # Available colors, e.g. "Navy Blue,Black,White"
    available_colors = Column(String(100), nullable=False, default="Multi")
    material = Column(String(50), nullable=True)  # Cotton, Silk, Denim, etc.
    price = Column(Float, nullable=False)  # Real selling price
    original_price = Column(Float, nullable=True)  # For showing discounts (e.g. 1999 -> 999)
    stock = Column(Integer, nullable=False, default=50)
    rating = Column(Float, default=4.2)
    rating_count = Column(Integer, default=120)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.CONFIRMED, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_title = Column(String(150), nullable=False)
    size = Column(String(20), nullable=False)
    color = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
