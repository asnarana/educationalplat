"""
Test script to verify Oracle Database connection and configuration.
Run this to check if your Oracle setup is correct.
"""
import os
import sys

print("=" * 60)
print("Oracle Database Connection Test")
print("=" * 60)

# Check environment variables
print("\n1. Checking Environment Variables:")
print("-" * 40)
oracle_user = os.getenv("ORACLE_USER", "NOT SET")
oracle_password = os.getenv("ORACLE_PASSWORD", "NOT SET")
oracle_host = os.getenv("ORACLE_HOST", "localhost")
oracle_port = os.getenv("ORACLE_PORT", "1521")
oracle_service = os.getenv("ORACLE_SERVICE_NAME", "XE")

print(f"ORACLE_USER: {oracle_user}")
print(f"ORACLE_PASSWORD: {'*' * len(oracle_password) if oracle_password != 'NOT SET' else 'NOT SET'}")
print(f"ORACLE_HOST: {oracle_host}")
print(f"ORACLE_PORT: {oracle_port}")
print(f"ORACLE_SERVICE_NAME: {oracle_service}")

if oracle_user == "NOT SET" or oracle_password == "NOT SET":
    print("\n⚠️  WARNING: ORACLE_USER and/or ORACLE_PASSWORD not set!")
    print("Please set them before running your app:")
    print('  $env:ORACLE_USER="your_username"')
    print('  $env:ORACLE_PASSWORD="your_password"')
    sys.exit(1)

# Check if oracledb is installed
print("\n2. Checking Python Oracle Driver:")
print("-" * 40)
try:
    import oracledb
    print(f"✅ oracledb version: {oracledb.__version__}")
except ImportError:
    print("❌ oracledb not installed!")
    print("Install it with: pip install oracledb")
    sys.exit(1)

# Test connection
print("\n3. Testing Database Connection:")
print("-" * 40)
try:
    # Test basic connection
    connection = oracledb.connect(
        user=oracle_user,
        password=oracle_password,
        host=oracle_host,
        port=int(oracle_port),
        service_name=oracle_service
    )
    print("✅ Connection successful!")
    
    # Get database version
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM v$version WHERE banner LIKE 'Oracle%'")
    version = cursor.fetchone()
    if version:
        print(f"✅ Database Version: {version[0]}")
    
    # Test if we can create a simple table (will drop if exists)
    try:
        cursor.execute("DROP TABLE test_connection_table")
    except:
        pass
    
    cursor.execute("""
        CREATE TABLE test_connection_table (
            id NUMBER PRIMARY KEY,
            test_data VARCHAR2(50)
        )
    """)
    cursor.execute("INSERT INTO test_connection_table VALUES (1, 'Connection Test')")
    connection.commit()
    print("✅ Table creation and insert test successful!")
    
    cursor.execute("DROP TABLE test_connection_table")
    connection.commit()
    print("✅ Table cleanup successful!")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ Connection failed: {str(e)}")
    print("\nCommon issues:")
    print("- Oracle service not running")
    print("- Wrong username/password")
    print("- Wrong service name (try 'XE' for Express Edition or 'FREEPDB1' for Oracle Free)")
    print("- Wrong host/port")
    print("- Firewall blocking connection")
    sys.exit(1)

# Test SQLAlchemy connection
print("\n4. Testing SQLAlchemy Connection:")
print("-" * 40)
try:
    from sqlalchemy import create_engine, text
    
    connection_string = (
        f"oracle+oracledb://{oracle_user}:{oracle_password}@"
        f"{oracle_host}:{oracle_port}/?service_name={oracle_service}"
    )
    
    engine = create_engine(connection_string, pool_pre_ping=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 FROM DUAL"))
        row = result.fetchone()
        if row:
            print("✅ SQLAlchemy connection successful!")
    
    engine.dispose()
    
except Exception as e:
    print(f"❌ SQLAlchemy connection failed: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Oracle Database is configured correctly.")
print("=" * 60)
print("\nYou can now start your application:")
print("  .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")

