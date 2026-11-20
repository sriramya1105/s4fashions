"""
S4 Fashions - Admin Provisioning CLI Tool
Usage:
    python scripts/create_admin.py --promote <username>
    python scripts/create_admin.py --create <username> --email <email> --password <password> --name <fullname>
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.models.entities import User, UserRole
from app.core.security import get_password_hash

def promote_user(username: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"[-] User '{username}' not found in database.")
            return False
        user.role = UserRole.ADMIN
        db.commit()
        print(f"[+] Successfully promoted user '{username}' to role ADMIN.")
        return True
    finally:
        db.close()

def create_admin(username: str, email: str, password: str, full_name: str = "Administrator"):
    db = SessionLocal()
    try:
        existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            print(f"[-] Username '{username}' or email '{email}' already exists.")
            return False
        
        new_admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            full_name=full_name
        )
        db.add(new_admin)
        db.commit()
        print(f"[+] Administrator account '{username}' created successfully.")
        return True
    finally:
        db.close()

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n--- Current Users in Database ---")
        for u in users:
            print(f"ID: {u.id:2d} | Username: {u.username:15s} | Role: {u.role.value:10s} | Email: {u.email}")
        print("---------------------------------\n")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage S4 Fashions Admin Accounts")
    parser.add_argument("--list", action="store_true", help="List all users and their roles")
    parser.add_argument("--promote", type=str, help="Promote an existing user to Admin")
    parser.add_argument("--create", type=str, help="Username for a new Admin")
    parser.add_argument("--email", type=str, help="Email for the new Admin")
    parser.add_argument("--password", type=str, help="Password for the new Admin")
    parser.add_argument("--name", type=str, default="Administrator", help="Full name for the new Admin")

    args = parser.parse_args()

    if args.list:
        list_users()
    elif args.promote:
        promote_user(args.promote)
    elif args.create:
        if not args.email or not args.password:
            print("[-] Both --email and --password are required when creating a new admin.")
            sys.exit(1)
        create_admin(args.create, args.email, args.password, args.name)
    else:
        list_users()
        parser.print_help()
