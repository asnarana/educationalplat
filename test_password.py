"""Test password hashing."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from passlib.context import CryptContext

print("Testing password hashing directly...")
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    test_password = "123"
    print(f"Password to hash: '{test_password}'")
    print(f"Password length: {len(test_password)} bytes")
    
    hash_val = pwd_context.hash(test_password)
    print(f"Hash created: {hash_val[:50]}...")
    
    verify_result = pwd_context.verify(test_password, hash_val)
    print(f"Verification: {verify_result}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
