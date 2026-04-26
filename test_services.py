"""
Integration test script to verify all service uploads work correctly
"""
import sys
from datetime import datetime
from models.db import db
from services.auth_service import AuthService
from services.product_service import ProductService
from services.stock_service import StockService
from services.plaza_service import PlazaService
from services.returns_services import ReturnsService
from services.sending_services import SendingService

# Test user ID (assume exists in database)
TEST_USER_ID = 1

def test_database_connection():
    """Test database connectivity"""
    print("🔌 Testing database connection...")
    try:
        if db.ping():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def test_product_creation():
    """Test product creation"""
    print("\n📦 Testing product creation...")
    try:
        product_service = ProductService(db)
        
        # Check if product already exists
        products = product_service.get_all()
        if not products:
            print("   No existing products, creating test product...")
            product = product_service.create_product(
                TEST_USER_ID,
                f"Test Product {datetime.now().timestamp()}",
                "Test Brand",
                "Test Description"
            )
            print(f"✅ Product created: ID={product['id']}, Name={product.get('name', 'N/A')}")
        else:
            print(f"✅ Found {len(products)} existing products")
            for p in products[:3]:
                print(f"   - {p.get('name', 'N/A')} (ID: {p['id']})")
        return True
    except Exception as e:
        print(f"❌ Product creation error: {str(e)}")
        return False

def test_stock_upload():
    """Test stock upload (most critical)"""
    print("\n📊 Testing stock upload...")
    try:
        stock_service = StockService(db)
        product_service = ProductService(db)
        
        # Get a product
        products = product_service.get_all()
        if not products:
            print("❌ No products available for stock test!")
            return False
        
        product = products[0]
        product_id = product['id']
        
        # Generate unique IMEI
        import random
        imei = str(random.randint(100000000000000, 999999999999999))
        
        print(f"   Adding stock to product ID={product_id}")
        print(f"   IMEI: {imei}")
        
        stock = stock_service.add_stock(
            TEST_USER_ID,
            product_id,
            imei,
            "Black",
            1
        )
        
        print(f"✅ Stock added successfully: ID={stock['id']}")
        
        # Verify aggregated stock view
        agg_stock = stock_service.get_aggregated_stock()
        print(f"   Aggregated stock records: {len(agg_stock)}")
        if agg_stock:
            print(f"   Sample: {agg_stock[0]}")
        
        return True
    except Exception as e:
        print(f"❌ Stock upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_plaza_sale():
    """Test plaza (sales) recording"""
    print("\n🛒 Testing plaza (sales) recording...")
    try:
        plaza_service = PlazaService(db)
        stock_service = StockService(db)
        product_service = ProductService(db)
        
        # Get a stock record
        agg_stock = stock_service.get_aggregated_stock()
        if not agg_stock:
            print("❌ No stock available for plaza test!")
            return False
        
        stock = agg_stock[0]
        product_id = stock['product_id']
        
        # Get the actual IMEI from the database
        imei_record = db.fetch_one(
            "SELECT imei FROM stock WHERE product_id=%s LIMIT 1",
            (product_id,)
        )
        
        if not imei_record:
            print("❌ Could not find IMEI for plaza test!")
            return False
        
        imei = imei_record['imei']
        
        print(f"   Recording sale: Product ID={product_id}, IMEI={imei}")
        
        plaza = plaza_service.record_sale(
            TEST_USER_ID,
            product_id,
            imei,
            1,
            "Test Customer",
            "1234567890"
        )
        
        print(f"✅ Sale recorded successfully: ID={plaza['id']}")
        
        # Verify all sales
        all_sales = plaza_service.get_all()
        print(f"   Total sales records: {len(all_sales)}")
        
        return True
    except Exception as e:
        print(f"❌ Plaza sale error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_returns():
    """Test returns recording"""
    print("\n↩️  Testing returns recording...")
    try:
        returns_service = ReturnsService(db)
        stock_service = StockService(db)
        
        # Get a stock record
        agg_stock = stock_service.get_aggregated_stock()
        if not agg_stock:
            print("❌ No stock available for returns test!")
            return False
        
        stock = agg_stock[0]
        product_id = stock['product_id']
        imei = stock['colour']  # Using colour as placeholder for now
        
        # Get actual IMEI
        imei_record = db.fetch_one(
            "SELECT imei, colour FROM stock WHERE product_id=%s LIMIT 1",
            (product_id,)
        )
        
        if not imei_record:
            print("❌ Could not find IMEI for returns test!")
            return False
        
        imei = imei_record['imei']
        colour = imei_record['colour']
        
        print(f"   Recording return: Product ID={product_id}, IMEI={imei}")
        
        ret = returns_service.create_return(
            TEST_USER_ID,
            product_id,
            imei,
            colour,
            1,
            "Defective unit"
        )
        
        print(f"✅ Return recorded successfully: ID={ret['id']}")
        
        # Verify all returns
        all_returns = returns_service.get_all()
        print(f"   Total return records: {len(all_returns)}")
        
        return True
    except Exception as e:
        print(f"❌ Returns error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_sending():
    """Test sending (dispatch) recording"""
    print("\n📤 Testing sending (dispatch) recording...")
    try:
        sending_service = SendingService(db)
        product_service = ProductService(db)
        
        # Get a product
        products = product_service.get_all()
        if not products:
            print("❌ No products available for sending test!")
            return False
        
        product = products[0]
        product_id = product['id']
        
        print(f"   Recording dispatch: Product ID={product_id}")
        
        sending = sending_service.create_dispatch(
            TEST_USER_ID,
            product_id,
            5,
            "9876543210",
            "Test dispatch"
        )
        
        print(f"✅ Dispatch recorded successfully: ID={sending['id']}")
        
        # Verify all sending records
        all_sending = sending_service.get_all()
        print(f"   Total dispatch records: {len(all_sending)}")
        
        return True
    except Exception as e:
        print(f"❌ Sending error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🧪 RETAILMAN - SERVICE INTEGRATION TEST")
    print("=" * 60)
    
    results = {
        "Database Connection": test_database_connection(),
        "Product Creation": test_product_creation(),
        "Stock Upload": test_stock_upload(),
        "Plaza (Sales)": test_plaza_sale(),
        "Returns": test_returns(),
        "Sending (Dispatch)": test_sending(),
    }
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
