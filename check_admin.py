"""Quick script to check admin user and test password."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.db import SessionLocal
from app.models import User

db = SessionLocal()
try:
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        print("Admin user found:")
        print(f"   ID: {admin.id}")
        print(f"   Username: {admin.username}")
        print(f"   Role: {admin.role}")
        print(f"   Password hash: {admin.password_hash[:50]}...")
        
        # Test password verification
        test_password = "123"
        is_valid = admin.verify_password(test_password)
        print(f"\nTesting password '123':")
        print(f"   Result: {'VALID' if is_valid else 'INVALID'}")
        
        # Try to hash a new password
        print(f"\nTesting password hashing:")
        try:
            new_hash = User.hash_password("123")
            print(f"   Hash created successfully: {new_hash[:50]}...")
            
            # Verify the new hash
            test_user = User(username="test", password_hash=new_hash, role="student")
            if test_user.verify_password("123"):
                print(f"   New hash verification works!")
            else:
                print(f"   New hash verification FAILED!")
        except Exception as e:
            print(f"   Error hashing: {e}")
    else:
        print("Admin user NOT found in database")
        print("   Creating admin user now...")
        try:
            admin_user = User(
                username="admin",
                password_hash=User.hash_password("123"),
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("   Admin user created successfully!")
        except Exception as e:
            print(f"   Error creating admin: {e}")
finally:
    db.close()
