"""
Test script to verify Oracle database connection and configuration.
"""
import os
import sys

print("=" * 60)
print("Oracle Database Connection Test")
print("=" * 60)

# Check if oracledb is installed
try:
    import oracledb
    print(f"[OK] oracledb module found: version {oracledb.__version__}")
except ImportError:
    print("[ERROR] oracledb module NOT installed")
    print("   Install with: pip install oracledb")
    sys.exit(1)

# Get configuration from environment or defaults
ORACLE_USER = os.getenv("ORACLE_USER", "system")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "Oracle123")
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = os.getenv("ORACLE_PORT", "1521")
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "FREEPDB1")

print(f"\nConfiguration:")
print(f"  Host: {ORACLE_HOST}")
print(f"  Port: {ORACLE_PORT}")
print(f"  Service: {ORACLE_SERVICE}")
print(f"  User: {ORACLE_USER}")
print(f"  Password: {'*' * len(ORACLE_PASSWORD)}")

# Build DSN
dsn = f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={ORACLE_HOST})(PORT={ORACLE_PORT}))(CONNECT_DATA=(SERVICE_NAME={ORACLE_SERVICE})))"

print(f"\nDSN: {dsn}")

# Test connection
print(f"\nAttempting connection...")
try:
    connection = oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=dsn
    )
    print("[OK] Connection successful!")
    
    # Test query
    cursor = connection.cursor()
    cursor.execute("SELECT banner FROM v$version WHERE banner LIKE 'Oracle%'")
    version = cursor.fetchone()
    print(f"[OK] Oracle version: {version[0]}")
    
    # Check if tables exist
    cursor.execute("""
        SELECT table_name FROM user_tables 
        WHERE table_name IN ('QUESTIONS', 'QUIZZES', 'ATTEMPTS')
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n[OK] Found {len(tables)} existing tables:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("\n[INFO] No tables found yet (database is empty)")
    
    # Check sequences
    cursor.execute("""
        SELECT sequence_name FROM user_sequences 
        WHERE sequence_name IN ('QUESTION_ID_SEQ', 'QUIZ_ID_SEQ', 'ATTEMPT_ID_SEQ')
        ORDER BY sequence_name
    """)
    sequences = cursor.fetchall()
    
    if sequences:
        print(f"\n[OK] Found {len(sequences)} existing sequences:")
        for seq in sequences:
            print(f"   - {seq[0]}")
    else:
        print("\n[INFO] No sequences found yet")
    
    cursor.close()
    connection.close()
    print("\n[OK] All checks passed! Oracle is ready to use.")
    
except oracledb.Error as e:
    error, = e.args
    print(f"\n[ERROR] Connection failed!")
    print(f"   Error code: {error.code}")
    print(f"   Error message: {error.message}")
    
    if error.code == 12514:
        print("\n[TIP] TNS Error 12514: Service name not registered with listener")
        print("   Possible solutions:")
        print("   1. Check if service name is correct (current: FREEPDB1)")
        print("   2. Verify Oracle listener is running")
        print("   3. Check listener.ora configuration")
        print("   4. Try connecting to CDB instead: ORACLE_SERVICE=ORCLCDB")
    elif error.code == 1017:
        print("\n[TIP] Error 1017: Invalid username/password")
        print("   Check your ORACLE_USER and ORACLE_PASSWORD environment variables")
    elif error.code == 12541:
        print("\n[TIP] Error 12541: TNS no listener")
        print("   Oracle listener is not running on port 1521")
    else:
        print(f"\n[TIP] Check Oracle configuration and ensure:")
        print("   - Oracle Database is running")
        print("   - Listener is running on port 1521")
        print("   - Service name is correct")
    
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)

