import os
import psycopg2
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models.entities import User, Category, SubCategory, Product, UserRole
from app.core.security import get_password_hash


def seed_postgres():
    print("[*] Creating all tables dynamically in PostgreSQL (s4fashions)...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 1. Seed Users (Admin & Customer)
    if db.query(User).count() == 0:
        print("[*] Seeding default Admin and Customer accounts...")
        admin = User(
            username="admin_user",
            email="admin@s4fashions.com",
            hashed_password=get_password_hash("Admin@ThreadCraft2026!"),
            role=UserRole.ADMIN,
            full_name="Master Merchandiser Admin"
        )
        customer = User(
            username="alice_customer",
            email="alice@example.com",
            hashed_password=get_password_hash("AlicePassword123!"),
            role=UserRole.CUSTOMER,
            full_name="Alice Sharma"
        )
        db.add_all([admin, customer])
        db.commit()

    # 2. Seed Dynamic 3 Round Categories: Men, Women, Kids
    if db.query(Category).count() == 0:
        print("[*] Seeding 3 Main Categories (Men, Women, Kids)...")
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
            description="Comfortable Festive Ethnic & Western Outfits for Kids",
            image_url="https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=400"
        )
        db.add_all([cat_men, cat_women, cat_kids])
        db.commit()

        # 3. Seed Connected Subcategories (e.g. Trousers under Men)
        print("[*] Seeding Subcategories connected to Categories...")
        subcats = [
            # Under Men
            SubCategory(category_id=cat_men.id, name="Trousers & Pants", slug="trousers", description="Formal trousers & casual chinos"),
            SubCategory(category_id=cat_men.id, name="Traditional Kurtas", slug="traditional-kurtas", description="Festive handloom kurtas & dhotis"),
            SubCategory(category_id=cat_men.id, name="Formal Shirts", slug="formal-shirts", description="Slim fit & executive cotton shirts"),
            SubCategory(category_id=cat_men.id, name="Denim Jeans", slug="denim-jeans", description="Stretch & classic fit denim"),

            # Under Women
            SubCategory(category_id=cat_women.id, name="Ethnic Sarees", slug="ethnic-sarees", description="Banarasi, Kanjeevaram & silk sarees"),
            SubCategory(category_id=cat_women.id, name="Kurtis & Anarkalis", slug="kurtis-anarkalis", description="Straight cut & flared designer kurtis"),
            SubCategory(category_id=cat_women.id, name="Short Tops & Tees", slug="short-tops", description="Casual crop tops, tees & western wear"),

            # Under Kids
            SubCategory(category_id=cat_kids.id, name="Boys Festive Sets", slug="boys-festive", description="Kurta dhoti & jacket sets"),
            SubCategory(category_id=cat_kids.id, name="Girls Frocks & Dresses", slug="girls-frocks", description="Layered party frocks & western dresses"),
            SubCategory(category_id=cat_kids.id, name="Infants & Toddlers", slug="infants-toddlers", description="Organic cotton rompers & sleepsuits"),
        ]
        db.add_all(subcats)
        db.commit()

    # 4. Seed Dynamic Products
    if db.query(Product).count() == 0:
        print("[*] Seeding Products linked to Categories and Subcategories...")
        cat_men = db.query(Category).filter(Category.slug == "men").first()
        cat_women = db.query(Category).filter(Category.slug == "women").first()
        cat_kids = db.query(Category).filter(Category.slug == "kids").first()

        sub_trousers = db.query(SubCategory).filter(SubCategory.slug == "trousers").first()
        sub_kurtas = db.query(SubCategory).filter(SubCategory.slug == "traditional-kurtas").first()
        sub_shirts = db.query(SubCategory).filter(SubCategory.slug == "formal-shirts").first()
        sub_jeans = db.query(SubCategory).filter(SubCategory.slug == "denim-jeans").first()

        sub_sarees = db.query(SubCategory).filter(SubCategory.slug == "ethnic-sarees").first()
        sub_kurtis = db.query(SubCategory).filter(SubCategory.slug == "kurtis-anarkalis").first()
        sub_tops = db.query(SubCategory).filter(SubCategory.slug == "short-tops").first()

        sub_boys = db.query(SubCategory).filter(SubCategory.slug == "boys-festive").first()
        sub_girls = db.query(SubCategory).filter(SubCategory.slug == "girls-frocks").first()
        sub_infants = db.query(SubCategory).filter(SubCategory.slug == "infants-toddlers").first()

        prods = [
            # Men
            Product(
                title="Raymond Executive Charcoal Slim Fit Formal Trousers",
                description="Wrinkle-resistant poly-viscose formal trousers designed for business wear with comfort flex waistband.",
                brand="Raymond",
                category_id=cat_men.id,
                subcategory_id=sub_trousers.id,
                available_sizes="30,32,34,36,38",
                available_colors="Charcoal Grey,Jet Black,Navy",
                material="Poly-Viscose Blend",
                price=1499.0,
                original_price=2299.0,
                stock=40,
                rating=4.6,
                rating_count=320,
                image_url="https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600"
            ),
            Product(
                title="FabIndia Pure Linen Straight Festive Kurta",
                description="Breathable handloom mandarin collar festive kurta in soothing royal cream.",
                brand="FabIndia",
                category_id=cat_men.id,
                subcategory_id=sub_kurtas.id,
                available_sizes="S,M,L,XL,XXL",
                available_colors="Ivory Cream,Maroon,Royal Blue",
                material="100% Pure Linen",
                price=1899.0,
                original_price=2799.0,
                stock=50,
                rating=4.7,
                rating_count=410,
                image_url="https://images.unsplash.com/photo-1597983073493-88cd35cf93b0?w=600"
            ),
            Product(
                title="Peter England Men Non-Iron Formal Oxford Shirt",
                description="Classic semi-cutaway pinpoint oxford cotton shirt with French cuffs.",
                brand="Peter England",
                category_id=cat_men.id,
                subcategory_id=sub_shirts.id,
                available_sizes="38,40,42,44",
                available_colors="Sky Blue,White,Lilac",
                material="100% Giza Cotton",
                price=1199.0,
                original_price=1799.0,
                stock=65,
                rating=4.4,
                rating_count=520,
                image_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600"
            ),
            Product(
                title="Levi's 511 Slim Fit Stretch Denim Trousers & Jeans",
                description="Modern slim cut jeans engineered with comfort stretch elastane.",
                brand="Levi's",
                category_id=cat_men.id,
                subcategory_id=sub_jeans.id,
                available_sizes="30,32,34,36",
                available_colors="Dark Indigo,Washed Black",
                material="Cotton Denim Stretch",
                price=2499.0,
                original_price=3599.0,
                stock=55,
                rating=4.8,
                rating_count=840,
                image_url="https://images.unsplash.com/photo-1542272604-780c96856592?w=600"
            ),
            Product(
                title="Manyavar Zari Embroidered Silk Kurta Churidar Set",
                description="Grand celebration attire with fine jacquard embroidery and churidar pyjama.",
                brand="Manyavar",
                category_id=cat_men.id,
                subcategory_id=sub_kurtas.id,
                available_sizes="M,L,XL",
                available_colors="Gold,Wine Red,Bottle Green",
                material="Art Silk Blend",
                price=4499.0,
                original_price=6499.0,
                stock=25,
                rating=4.9,
                rating_count=190,
                image_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600"
            ),

            # Women
            Product(
                title="Heritage Weaves Banarasi Katan Silk Floral Saree",
                description="Authentic gold zari kadwa floral weave with rich pallu border.",
                brand="Heritage Weaves",
                category_id=cat_women.id,
                subcategory_id=sub_sarees.id,
                available_sizes="5.5m + Blouse",
                available_colors="Emerald Green,Crimson Red,Royal Violet",
                material="Pure Katan Silk",
                price=5499.0,
                original_price=7999.0,
                stock=18,
                rating=4.9,
                rating_count=230,
                image_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600"
            ),
            Product(
                title="Biba Flared Anarkali Kurti with Dupatta",
                description="Floral printed chanderi cotton Anarkali silhouette with gotapatti detailing.",
                brand="Biba",
                category_id=cat_women.id,
                subcategory_id=sub_kurtis.id,
                available_sizes="XS,S,M,L,XL",
                available_colors="Teal Blue,Dusty Rose,Mustard",
                material="Chanderi Cotton",
                price=2199.0,
                original_price=3299.0,
                stock=35,
                rating=4.7,
                rating_count=450,
                image_url="https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600"
            ),
            Product(
                title="W for Woman Straight Rayon Daily Kurti",
                description="Contemporary geometric motif straight-cut kurti with notch collar.",
                brand="W for Woman",
                category_id=cat_women.id,
                subcategory_id=sub_kurtis.id,
                available_sizes="S,M,L,XL,XXL",
                available_colors="Coral,Olive,Navy",
                material="Soft Viscose Rayon",
                price=899.0,
                original_price=1499.0,
                stock=70,
                rating=4.5,
                rating_count=380,
                image_url="https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600"
            ),
            Product(
                title="Zara Ribbed Square Neck Crop Short Top",
                description="Knitted stretch short top with lettuce edge trim. Pairs perfectly with high-waist trousers.",
                brand="Zara",
                category_id=cat_women.id,
                subcategory_id=sub_tops.id,
                available_sizes="XS,S,M,L",
                available_colors="Lavender,Black,White,Mint",
                material="Ribbed Cotton Spandex",
                price=799.0,
                original_price=1290.0,
                stock=80,
                rating=4.4,
                rating_count=590,
                image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600"
            ),
            Product(
                title="H&M Floral Crepe Tiered Short Western Dress",
                description="Deep V-neck wrap front short dress with tie belt and ruffled flutter sleeves.",
                brand="H&M",
                category_id=cat_women.id,
                subcategory_id=sub_tops.id,
                available_sizes="XS,S,M,L",
                available_colors="Pastel Yellow,Floral Black",
                material="Viscose Crepe",
                price=1699.0,
                original_price=2499.0,
                stock=45,
                rating=4.6,
                rating_count=310,
                image_url="https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600"
            ),

            # Kids
            Product(
                title="Hopscotch Boys Cotton Kurta Dhoti Trouser Set",
                description="Elasticated waistband traditional dhoti pant paired with jacquard embroidered buttoned kurta.",
                brand="Hopscotch",
                category_id=cat_kids.id,
                subcategory_id=sub_boys.id,
                available_sizes="2-3Y,4-5Y,6-7Y,8-9Y",
                available_colors="Yellow Gold,Sky Blue",
                material="100% Combed Cotton",
                price=999.0,
                original_price=1599.0,
                stock=60,
                rating=4.6,
                rating_count=220,
                image_url="https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=600"
            ),
            Product(
                title="Mini Klub Girls Layered Star Party Frock Dress",
                description="Tiered net tulle party frock with soft satin lining and glitter accents.",
                brand="Mini Klub",
                category_id=cat_kids.id,
                subcategory_id=sub_girls.id,
                available_sizes="1-2Y,3-4Y,5-6Y",
                available_colors="Princess Pink,Baby Blue",
                material="Tulle & Satin",
                price=1299.0,
                original_price=1899.0,
                stock=40,
                rating=4.8,
                rating_count=290,
                image_url="https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=600"
            ),
            Product(
                title="Mothercare Unisex Infant Organic Cotton Rompers (3-Pack)",
                description="Ultra-soft popper fastening footed sleepsuits made from 100% chemical-free organic cotton.",
                brand="Mothercare",
                category_id=cat_kids.id,
                subcategory_id=sub_infants.id,
                available_sizes="0-3M,3-6M,6-12M",
                available_colors="Pastel Multi",
                material="100% Organic Cotton",
                price=1199.0,
                original_price=1699.0,
                stock=75,
                rating=4.9,
                rating_count=380,
                image_url="https://images.unsplash.com/photo-1522771930-78848d9293e8?w=600"
            ),
        ]
        db.add_all(prods)
        db.commit()

    print("[+] Database initialized & seeded successfully with dynamic models!")
    db.close()


if __name__ == "__main__":
    seed_postgres()
