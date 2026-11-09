import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models.entities import User, Product, UserRole, ProductCategory
from app.core.security import get_password_hash


def seed_database():
    print("[*] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 1. Seed Users (Admin & Customers)
    if db.query(User).count() == 0:
        print("[*] Seeding default users (Customer & Admin)...")
        users = [
            User(
                username="admin_user",
                email="admin@threadcraft.com",
                hashed_password=get_password_hash("Admin@ThreadCraft2026!"),
                role=UserRole.ADMIN,
                full_name="Chief Merchandiser",
            ),
            User(
                username="alice_customer",
                email="alice@example.com",
                hashed_password=get_password_hash("AlicePassword123!"),
                role=UserRole.CUSTOMER,
                full_name="Alice Sharma",
            ),
            User(
                username="bob_customer",
                email="bob@example.com",
                hashed_password=get_password_hash("BobPassword123!"),
                role=UserRole.CUSTOMER,
                full_name="Bob Kumar",
            ),
        ]
        db.add_all(users)
        db.commit()

    # 2. Seed Products (Men, Women, Kids Apparel)
    if db.query(Product).count() == 0:
        print("[*] Seeding Men, Women, and Kids clothing catalog...")
        products = [
            # === MEN'S TRADITIONAL ===
            Product(
                title="FabIndia Pure Cotton Straight Kurta",
                description="Crafted from hand-spun breathable cotton, this knee-length mandarin collar kurta is perfect for festive occasions and casual traditional wear.",
                brand="FabIndia",
                category=ProductCategory.MEN,
                subcategory="Traditional",
                available_sizes="S,M,L,XL,XXL",
                available_colors="Maroon,Off-White,Royal Blue",
                material="100% Pure Cotton",
                price=1299.0,
                original_price=1899.0,
                stock=45,
                rating=4.5,
                rating_count=320,
                image_url="https://images.unsplash.com/photo-1597983073493-88cd35cf93b0?w=600",
            ),
            Product(
                title="Manyavar Embroidered Silk Blend Sherwani Set",
                description="Luxurious Jacquard silk blend sherwani accompanied by churidar trousers. Detailed zari embroidery around the collar and cuffs.",
                brand="Manyavar",
                category=ProductCategory.MEN,
                subcategory="Traditional",
                available_sizes="M,L,XL",
                available_colors="Gold,Cream,Wine Red",
                material="Silk Blend",
                price=4999.0,
                original_price=6999.0,
                stock=20,
                rating=4.8,
                rating_count=145,
                image_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600",
            ),
            Product(
                title="Ramraj Cotton Traditional Dhoti & Angavastram Set",
                description="Fine combed gold-bordered pure cotton white dhoti and matching angavastram for temple visits and traditional rituals.",
                brand="Ramraj Cotton",
                category=ProductCategory.MEN,
                subcategory="Traditional",
                available_sizes="Free Size",
                available_colors="Pure White",
                material="Combed Cotton",
                price=850.0,
                original_price=1100.0,
                stock=60,
                rating=4.6,
                rating_count=210,
                image_url="https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600",
            ),

            # === MEN'S MODERN ===
            Product(
                title="Peter England Men Slim Fit Formal Shirt",
                description="Wrinkle-resistant pinpoint oxford cotton shirt with semi-cutaway collar and buttoned French cuffs.",
                brand="Peter England",
                category=ProductCategory.MEN,
                subcategory="Modern",
                available_sizes="38,40,42,44",
                available_colors="Sky Blue,Classic White,Light Pink",
                material="Poly-Cotton",
                price=1149.0,
                original_price=1599.0,
                stock=75,
                rating=4.3,
                rating_count=480,
                image_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600",
            ),
            Product(
                title="Levi's 511 Slim Fit Stretch Denim Jeans",
                description="Iconic slim cut with room to move. Premium heavyweight denim infused with 2% elastane for maximum daily comfort.",
                brand="Levi's",
                category=ProductCategory.MEN,
                subcategory="Modern",
                available_sizes="30,32,34,36",
                available_colors="Dark Indigo,Faded Black,Stonewash Blue",
                material="Cotton Stretch Denim",
                price=2499.0,
                original_price=3599.0,
                stock=55,
                rating=4.6,
                rating_count=690,
                image_url="https://images.unsplash.com/photo-1542272604-780c96856592?w=600",
            ),
            Product(
                title="Allen Solly Men Solid Polo T-Shirt",
                description="Signature pique honeycomb knit polo with contrasting inner placket and embroidered brand crest.",
                brand="Allen Solly",
                category=ProductCategory.MEN,
                subcategory="Modern",
                available_sizes="S,M,L,XL",
                available_colors="Forest Green,Navy,Mustard Yellow",
                material="100% Pique Cotton",
                price=899.0,
                original_price=1299.0,
                stock=80,
                rating=4.2,
                rating_count=310,
                image_url="https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600",
            ),

            # === WOMEN'S ETHNIC & TRADITIONAL ===
            Product(
                title="Biba Flared Anarkali Kurta with Dupatta Set",
                description="Floral printed chanderi cotton Anarkali silhouette with gotapatti detailing along neckline, paired with sheer dupatta.",
                brand="Biba",
                category=ProductCategory.WOMEN,
                subcategory="Ethnic",
                available_sizes="XS,S,M,L,XL",
                available_colors="Teal Green,Dusty Rose,Indigo",
                material="Chanderi Cotton",
                price=2299.0,
                original_price=3499.0,
                stock=35,
                rating=4.7,
                rating_count=520,
                image_url="https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600",
            ),
            Product(
                title="Sabyasachi Heritage Banarasi Silk Saree",
                description="Woven in the heart of Varanasi with gold zari floral kadwa weave and broad contrast pallu border.",
                brand="Heritage Weaves",
                category=ProductCategory.WOMEN,
                subcategory="Traditional",
                available_sizes="5.5m + Blouse",
                available_colors="Emerald Green,Deep Red,Royal Purple",
                material="Pure Katan Silk",
                price=5899.0,
                original_price=8500.0,
                stock=15,
                rating=4.9,
                rating_count=190,
                image_url="https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600",
            ),
            Product(
                title="W for Woman Straight Rayon Daily Kurti",
                description="Contemporary geometric motif straight-cut kurti with three-quarter bell sleeves and notch collar.",
                brand="W for Woman",
                category=ProductCategory.WOMEN,
                subcategory="Kurtis",
                available_sizes="S,M,L,XL,XXL",
                available_colors="Mustard,Olive,Coral",
                material="Soft Viscose Rayon",
                price=849.0,
                original_price=1399.0,
                stock=60,
                rating=4.4,
                rating_count=430,
                image_url="https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=600",
            ),

            # === WOMEN'S SHORT TOPS & WESTERN ===
            Product(
                title="Zara Ribbed Crop Top & Short Tee",
                description="Square neckline stretch knitted short top with lettuce hem finish. Essential casual piece for high-rise jeans.",
                brand="Zara",
                category=ProductCategory.WOMEN,
                subcategory="Short Tops",
                available_sizes="XS,S,M,L",
                available_colors="Lavender,Black,White,Mint",
                material="Cotton Elastane Rib",
                price=799.0,
                original_price=1190.0,
                stock=90,
                rating=4.3,
                rating_count=610,
                image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600",
            ),
            Product(
                title="H&M Floral Print A-Line Wrap Dress",
                description="Short crepe dress featuring deep V-neck wrap front, tie belt at waist, and ruffled cap sleeves.",
                brand="H&M",
                category=ProductCategory.WOMEN,
                subcategory="Western",
                available_sizes="XS,S,M,L",
                available_colors="Floral Black,Pastel Yellow",
                material="Viscose Crepe",
                price=1799.0,
                original_price=2299.0,
                stock=40,
                rating=4.5,
                rating_count=280,
                image_url="https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600",
            ),

            # === KIDS' WEAR (Boys, Girls, Toddlers) ===
            Product(
                title="Hopscotch Boys Cotton Festive Kurta & Dhoti Pant Set",
                description="Comfortable pre-stitched elasticated waistband dhoti paired with jacquard embroidered buttoned kurta for boys.",
                brand="Hopscotch",
                category=ProductCategory.KIDS,
                subcategory="Boys Ethnic",
                available_sizes="2-3Y,4-5Y,6-7Y,8-9Y",
                available_colors="Yellow Gold,Sky Blue",
                material="Pure Cotton",
                price=999.0,
                original_price=1499.0,
                stock=50,
                rating=4.5,
                rating_count=180,
                image_url="https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=600",
            ),
            Product(
                title="Mini Klub Girls Layered Party Frock Dress",
                description="Tiered net tulle party frock with soft satin lining, glitter star accents, and satin back bow.",
                brand="Mini Klub",
                category=ProductCategory.KIDS,
                subcategory="Girls Western",
                available_sizes="1-2Y,3-4Y,5-6Y",
                available_colors="Princess Pink,Baby Blue",
                material="Soft Tulle & Satin",
                price=1299.0,
                original_price=1899.0,
                stock=30,
                rating=4.8,
                rating_count=240,
                image_url="https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=600",
            ),
            Product(
                title="Mothercare Unisex Infant Cotton Rompers (Pack of 3)",
                description="Ultra-soft nickel-free popper fastening footed sleepsuits with anti-scratch mittens. Chemical-free organic cotton.",
                brand="Mothercare",
                category=ProductCategory.KIDS,
                subcategory="Infants & Toddlers",
                available_sizes="0-3M,3-6M,6-12M",
                available_colors="Pastel Multi",
                material="100% Organic Cotton",
                price=1199.0,
                original_price=1699.0,
                stock=70,
                rating=4.9,
                rating_count=350,
                image_url="https://images.unsplash.com/photo-1522771930-78848d9293e8?w=600",
            ),
        ]
        db.add_all(products)
        db.commit()

    print("[+] Seed completed successfully! Database is ready with users and clothing catalog.")
    db.close()


if __name__ == "__main__":
    seed_database()
