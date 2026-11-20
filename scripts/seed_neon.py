import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Neon Connection URL provided by user (using psycopg2 driver)
NEON_URL = "postgresql+psycopg2://neondb_owner:npg_dxGQDbhaq6t5@ep-sparkling-mountain-bbqfqk8z-pooler.c-15.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("[*] Connecting to Neon Cloud PostgreSQL...")
engine = create_engine(NEON_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models
from app.db.session import Base
from app.models.entities import User, Category, SubCategory, Product, UserRole
from app.core.security import get_password_hash

print("[*] Creating all database tables in Neon...")
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 1. Seed Users
if db.query(User).count() == 0:
    print("[*] Seeding default Admin and Customer accounts...")
    admin = User(
        username="admin_user",
        email="admin@s4fashions.com",
        hashed_password=get_password_hash("Admin@ThreadCraft2026!"),
        role=UserRole.ADMIN,
        full_name="Master Merchandiser Admin"
    )
    admin_test = User(
        username="test",
        email="test@gmail.com",
        hashed_password=get_password_hash("Admin@ThreadCraft2026!"),
        role=UserRole.ADMIN,
        full_name="Merchant Admin"
    )
    customer = User(
        username="alice_customer",
        email="alice@example.com",
        hashed_password=get_password_hash("AlicePassword123!"),
        role=UserRole.CUSTOMER,
        full_name="Alice Sharma"
    )
    db.add_all([admin, admin_test, customer])
    db.commit()
    print("  -> Users seeded.")

# 2. Seed Categories
if db.query(Category).count() == 0:
    print("[*] Seeding Categories...")
    cat_men = Category(
        name="Men",
        slug="men",
        description="Premium Men's Traditional & Modern Wear",
        image_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=400"
    )
    cat_women = Category(
        name="Women",
        slug="women",
        description="Designer Sarees, Kurtis, and Modern Western Tops",
        image_url="https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=400"
    )
    cat_kids = Category(
        name="Kids",
        slug="kids",
        description="Festive Wear & Comfortable Daily Playwear for Boys, Girls, and Infants",
        image_url="https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=400"
    )
    db.add_all([cat_men, cat_women, cat_kids])
    db.commit()
    print("  -> Categories seeded.")

# 3. Seed Subcategories
cat_men = db.query(Category).filter(Category.slug == "men").first()
cat_women = db.query(Category).filter(Category.slug == "women").first()
cat_kids = db.query(Category).filter(Category.slug == "kids").first()

if db.query(SubCategory).count() == 0:
    print("[*] Seeding Subcategories...")
    subcategories = [
        SubCategory(name="Trousers & Pants", slug="trousers", category_id=cat_men.id, description="Slim-fit formal, casual trousers and chinos"),
        SubCategory(name="Traditional Kurtas", slug="men-kurtas", category_id=cat_men.id, description="Grand silk, linen and embroidered ethnic sets"),
        SubCategory(name="Formal Shirts", slug="formal-shirts", category_id=cat_men.id, description="Oxford, French cuff, and crisp non-iron button-downs"),
        SubCategory(name="Ethnic Sarees", slug="sarees", category_id=cat_women.id, description="Banarasi, Kanjeevaram and silk handwoven sarees"),
        SubCategory(name="Kurtis & Anarkalis", slug="kurtis", category_id=cat_women.id, description="Everyday straight cotton kurtis and festive tiered Anarkalis"),
        SubCategory(name="Short Tops & Tees", slug="women-tops", category_id=cat_women.id, description="Ribbed knit crop tops, flutter-sleeve floral crepe dresses"),
        SubCategory(name="Boys Festive Sets", slug="boys-festive", category_id=cat_kids.id, description="Embroidered kurta dhoti and jacket sets for boys"),
        SubCategory(name="Girls Frocks & Dresses", slug="girls-frocks", category_id=cat_kids.id, description="Tiered star tulle party frocks and ruffled dresses"),
        SubCategory(name="Infants & Toddlers", slug="infants-toddlers", category_id=cat_kids.id, description="100% organic soft cotton sleepsuits and rompers"),
    ]
    db.add_all(subcategories)
    db.commit()
    print("  -> Subcategories seeded.")

# 4. Seed Products
sub_map = {s.slug: s.id for s in db.query(SubCategory).all()}

if db.query(Product).count() == 0:
    print("[*] Seeding Products with dynamic specifications...")
    products = [
        Product(
            title="Raymond Executive Charcoal Slim Fit Formal Trousers",
            description="Wrinkle-resistant poly-viscose formal trousers designed for business wear with comfort flex waistband.",
            brand="Raymond",
            category_id=cat_men.id,
            subcategory_id=sub_map["trousers"],
            available_sizes="30,32,34,36,38",
            available_colors="Charcoal Grey,Jet Black,Navy",
            material="Poly-Viscose Blend",
            price=1499.00,
            original_price=2299.00,
            stock=40,
            rating=4.6,
            rating_count=320,
            image_url="https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600",
            specifications="Fit: Slim Fit, Fabric: Poly-Viscose Blend, Pattern: Solid, Closure: Button & Zip, Pocket: 4 Pockets, Rise: Mid Rise"
        ),
        Product(
            title="FabIndia Pure Linen Straight Festive Kurta",
            description="Breathable handloom mandarin collar festive kurta in soothing royal cream.",
            brand="FabIndia",
            category_id=cat_men.id,
            subcategory_id=sub_map["men-kurtas"],
            available_sizes="S,M,L,XL,XXL",
            available_colors="Ivory Cream,Maroon,Royal Blue",
            material="100% Pure Linen",
            price=1899.00,
            original_price=2799.00,
            stock=50,
            rating=4.7,
            rating_count=410,
            image_url="https://images.unsplash.com/photo-1597983073493-88cd35cf93b0?w=600",
            specifications="Color: Ivory Cream, Neck: Mandarin Collar, Sleeve: Full Sleeve, Length: Knee Length, Fabric: Pure Handloom Linen"
        ),
        Product(
            title="Peter England Men Non-Iron Formal Oxford Shirt",
            description="Classic semi-cutaway pinpoint oxford cotton shirt with French cuffs.",
            brand="Peter England",
            category_id=cat_men.id,
            subcategory_id=sub_map["formal-shirts"],
            available_sizes="38,40,42,44",
            available_colors="Sky Blue,White,Lilac",
            material="100% Giza Cotton",
            price=1199.00,
            original_price=1799.00,
            stock=65,
            rating=4.4,
            rating_count=520,
            image_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600",
            specifications="Fit: Regular Fit, Collar: Semi Cutaway, Cuff: Button Cuff, Pattern: Solid Oxford, Fabric: 100% Giza Cotton"
        ),
        Product(
            title="Manyavar Zari Embroidered Silk Kurta Churidar Set",
            description="Grand celebration attire with fine jacquard embroidery and churidar pyjama.",
            brand="Manyavar",
            category_id=cat_men.id,
            subcategory_id=sub_map["men-kurtas"],
            available_sizes="M,L,XL",
            available_colors="Gold,Wine Red,Bottle Green",
            material="Art Silk Blend",
            price=4499.00,
            original_price=6499.00,
            stock=25,
            rating=4.9,
            rating_count=190,
            image_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600",
            specifications="Occasion: Wedding & Festive, Top Fabric: Art Silk Blend, Bottom Type: Churidar, Embroidery: Zari Jacquard Work"
        ),
        Product(
            title="Heritage Weaves Banarasi Katan Silk Floral Saree",
            description="Authentic gold zari kadwa floral weave with rich pallu border.",
            brand="Heritage Weaves",
            category_id=cat_women.id,
            subcategory_id=sub_map["sarees"],
            available_sizes="5.5m + Blouse",
            available_colors="Emerald Green,Crimson Red,Royal Violet",
            material="Pure Katan Silk",
            price=5499.00,
            original_price=7999.00,
            stock=18,
            rating=4.9,
            rating_count=230,
            image_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600",
            specifications="Fabric: Pure Katan Silk, Blouse Piece: Included (0.8m), Border: Gold Zari Floral Kadwa, Saree Length: 5.5m"
        ),
        Product(
            title="Biba Flared Anarkali Kurti with Dupatta",
            description="Floral printed chanderi cotton Anarkali silhouette with gotapatti detailing.",
            brand="Biba",
            category_id=cat_women.id,
            subcategory_id=sub_map["kurtis"],
            available_sizes="XS,S,M,L,XL",
            available_colors="Teal Blue,Dusty Rose,Mustard",
            material="Chanderi Cotton",
            price=2199.00,
            original_price=3299.00,
            stock=35,
            rating=4.7,
            rating_count=450,
            image_url="https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600",
            specifications="Silhouette: Anarkali Flared, Fabric: Chanderi Cotton, Dupatta: Included, Detailing: Gotapatti Work, Length: Calf Length"
        ),
        Product(
            title="W for Woman Straight Rayon Daily Kurti",
            description="Contemporary geometric motif straight-cut kurti with notch collar.",
            brand="W for Woman",
            category_id=cat_women.id,
            subcategory_id=sub_map["kurtis"],
            available_sizes="S,M,L,XL,XXL",
            available_colors="Coral,Olive,Navy",
            material="Soft Viscose Rayon",
            price=899.00,
            original_price=1499.00,
            stock=70,
            rating=4.5,
            rating_count=380,
            image_url="https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600",
            specifications="Silhouette: Straight Cut, Neck: Notch Mandarin, Fabric: 100% Viscose Rayon, Slit: Side Slits, Sleeve: 3/4th Sleeve"
        ),
        Product(
            title="Zara Ribbed Square Neck Crop Short Top",
            description="Knitted stretch short top with lettuce edge trim. Pairs perfectly with high-waist trousers.",
            brand="Zara",
            category_id=cat_women.id,
            subcategory_id=sub_map["women-tops"],
            available_sizes="XS,S,M,L",
            available_colors="Lavender,Black,White,Mint",
            material="Ribbed Cotton Spandex",
            price=799.00,
            original_price=1290.00,
            stock=80,
            rating=4.4,
            rating_count=590,
            image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600",
            specifications="Fit: Bodycon Crop, Neck: Square Neck, Fabric: Ribbed Cotton Spandex, Hemline: Lettuce Edge, Sleeve: Sleeveless"
        ),
        Product(
            title="H&M Floral Crepe Tiered Short Western Dress",
            description="Deep V-neck wrap front short dress with tie belt and ruffled flutter sleeves.",
            brand="H&M",
            category_id=cat_women.id,
            subcategory_id=sub_map["women-tops"],
            available_sizes="XS,S,M,L",
            available_colors="Pastel Yellow,Floral Black",
            material="Viscose Crepe",
            price=1699.00,
            original_price=2499.00,
            stock=45,
            rating=4.6,
            rating_count=310,
            image_url="https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600",
            specifications="Style: Wrap Mini Dress, Neck: V-Neck, Pattern: Ditsy Floral, Fabric: 100% Viscose Crepe, Sleeve: Flutter Sleeve"
        ),
        Product(
            title="Hopscotch Boys Cotton Kurta Dhoti Trouser Set",
            description="Elasticated waistband traditional dhoti pant paired with jacquard embroidered buttoned kurta.",
            brand="Hopscotch",
            category_id=cat_kids.id,
            subcategory_id=sub_map["boys-festive"],
            available_sizes="2-3Y,4-5Y,6-7Y,8-9Y",
            available_colors="Yellow Gold,Sky Blue",
            material="100% Combed Cotton",
            price=999.00,
            original_price=1599.00,
            stock=60,
            rating=4.6,
            rating_count=220,
            image_url="https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=600",
            specifications="Age Group: 2Y-9Y, Set Contains: Kurta & Dhoti Trouser, Waistband: Full Elastic, Fabric: 100% Combed Cotton"
        ),
        Product(
            title="Mini Klub Girls Layered Star Party Frock Dress",
            description="Tiered net tulle party frock with soft satin lining and glitter accents.",
            brand="Mini Klub",
            category_id=cat_kids.id,
            subcategory_id=sub_map["girls-frocks"],
            available_sizes="1-2Y,3-4Y,5-6Y",
            available_colors="Princess Pink,Baby Blue",
            material="Tulle & Satin",
            price=1299.00,
            original_price=1899.00,
            stock=40,
            rating=4.8,
            rating_count=290,
            image_url="https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=600",
            specifications="Occasion: Birthday & Party, Layers: 3-Tier Net Tulle, Lining: 100% Soft Satin, Closure: Concealed Back Zip"
        ),
        Product(
            title="Mothercare Unisex Infant Organic Cotton Rompers (3-Pack)",
            description="Ultra-soft popper fastening footed sleepsuits made from 100% chemical-free organic cotton.",
            brand="Mothercare",
            category_id=cat_kids.id,
            subcategory_id=sub_map["infants-toddlers"],
            available_sizes="0-3M,3-6M,6-12M",
            available_colors="Pastel Multi",
            material="100% Organic Cotton",
            price=1199.00,
            original_price=1699.00,
            stock=75,
            rating=4.9,
            rating_count=380,
            image_url="https://images.unsplash.com/photo-1522771930-78848d9293e8?w=600",
            specifications="Pack Size: 3 Sleepsuits, Fastening: Nickel-Free Poppers, Fabric: 100% GOTS Certified Organic Cotton, Feet: Enclosed Footies"
        )
    ]
    db.add_all(products)
    db.commit()
    print("  -> Products seeded successfully.")

print("\n" + "="*60)
print("[SUCCESS] Neon Cloud PostgreSQL has been completely populated!")
print(f"Users: {db.query(User).count()}")
print(f"Categories: {db.query(Category).count()}")
print(f"Subcategories: {db.query(SubCategory).count()}")
print(f"Products: {db.query(Product).count()}")
print("="*60)
