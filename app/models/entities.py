from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text, Boolean
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# ==========================================
# 1. DYNAMIC CATEGORY TABLE
# ==========================================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "Men", "Women", "Kids"
    slug = Column(String(50), unique=True, nullable=False)  # e.g., "men", "women", "kids"
    description = Column(String(200), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    subcategories = relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


# ==========================================
# 2. DYNAMIC SUBCATEGORY TABLE (Connected to Category)
# ==========================================
class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(60), nullable=False)  # e.g., "Trousers", "Kurtis", "Short Tops"
    slug = Column(String(60), nullable=False)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")


# ==========================================
# 3. DYNAMIC PRODUCTS TABLE
# ==========================================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(180), nullable=False, index=True)
    description = Column(Text, nullable=False)
    brand = Column(String(60), nullable=False, index=True)
    
    # Dynamic Relational Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="SET NULL"), nullable=True, index=True)

    available_sizes = Column(String(120), nullable=False, default="S,M,L,XL")
    available_colors = Column(String(120), nullable=False, default="Black,White,Navy")
    material = Column(String(80), nullable=True)
    
    price = Column(Float, nullable=False)  # Selling price
    original_price = Column(Float, nullable=True)  # MRP for discount calculation
    stock = Column(Integer, nullable=False, default=50)
    rating = Column(Float, default=4.5)
    rating_count = Column(Integer, default=150)
    image_url = Column(String(500), nullable=True)
    color_images = Column(Text, nullable=True)  # JSON: {"Black": "https://...", "Navy": "https://..."}
    specifications = Column(Text, nullable=True)  # Dynamic specs e.g. "Color: Blue, Bottom: Black, Fit: Regular"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


# ==========================================
# 4. USERS & AUTHENTICATION TABLE
# ==========================================
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


# ==========================================
# 5. ORDERS & CHECKOUT TABLES
# ==========================================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(Text, nullable=False)
    phone_number = Column(String(25), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.CONFIRMED, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_title = Column(String(180), nullable=False)
    size = Column(String(30), nullable=False)
    color = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
