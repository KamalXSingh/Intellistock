from app.models.category import Category
from app.models.products import Product
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.models.suppliers import Supplier

def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to IntelliStock API",
        "status": "running"
    }


def test_get_products(client):
    response = client.get("/products/")

    assert response.status_code == 200
    assert isinstance(response.json(),list)

def test_get_products_with_data(client,db_session):    
    category= Category(
        name="Test Electronics",
        description="Testing category"
    )
    
    db_session.add(category)
    db_session.flush()
    
    product=Product(
        name="Test Mouse",
        price=999,
        sku="TEST-001",
        category_id=category.id
    )
    
    db_session.add(product)
    db_session.commit()
    
    response=client.get("/products/")
    
    assert response.status_code == 200
    data=response.json()
    
    assert len(data)==1
    assert data[0]["name"]=="Test Mouse"
    assert data[0]["sku"]=="TEST-001"
    assert data[0]["category"]["name"]=="Test Electronics"
  
def test_get_product_by_id(client,db_session):
    category=Category(
        name="Test Category",
        description="Testing"
    )
    
    db_session.add(category)
    db_session.flush()
    
    product = Product(
        name="Test Keyboard",
        price=1500,
        sku="TEST-002",
        category_id=category.id
    )
    
    db_session.add(product)
    db_session.commit()
    
    response = client.get(f"/products/{product.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Keyboard"
    assert data["sku"] == "TEST-002"
    assert data["category"]["name"] == "Test Category"

def test_get_product_not_found(client):
    response=client.get("/products/99999")
    
    assert response.status_code==404
    assert response.json()["message"]=="Product not found"

def test_database_rollback(db_session):
    category = Category(
        name="Pytest Temporary Category",
        description="Testing rollback"
    )

    db_session.add(category)
    db_session.commit()

    assert db_session.query(Category).filter(
        Category.name == "Pytest Temporary Category"
    ).first() is not None

def test_create_product(client, db_session):
    category = Category(
        name="Test Electronics",
        description="Testing category"
    )

    db_session.add(category)
    db_session.commit()

    response = client.post(
        "/products/",
        json={
            "name": "Test Mouse",
            "price": 999,
            "sku": "TEST-MOUSE-001",
            "description": "Testing product",
            "category_id": category.id
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Mouse"
    assert response.json()["sku"] == "TEST-MOUSE-001"
    assert response.json()["price"]==999
    assert response.json()["category"]["name"]=="Test Electronics"
    
    product = db_session.query(Product).filter(
       Product.sku == "TEST-MOUSE-001"
    ).first()

    assert product is not None
    assert product.name == "Test Mouse"
    
def test_create_product_duplicate_sku(client,db_session):
    category=Category(
        name="Duplicate Test Category",
        description="Testing duplicate SKU"
    )
    
    db_session.add(category)
    db_session.flush()
    
    product_data = {
        "name":"First Mouse",
        "price":999,
        "sku":"DUPLICATE-001",
        "category_id":category.id
    }
    
    first_response=client.post("/products/",json=product_data)
    
    assert first_response.status_code==200
    
    product_data["name"]="Second Mouse"

    
    second_response=client.post("/products/",json=product_data)
    
    assert second_response.status_code==409
    assert second_response.json()["message"]=="SKU already exists"

def test_create_product_invalid_category(client):
    product_data={
        "name":"Invalid Category Mouse",
        "price":999,
        "sku":"INVALID-CAT-001",
        "category_id":9999
    }
    
    response=client.post("/products/",json=product_data)
    
    assert response.status_code==409
    assert response.json()["message"]=="Invalid category_id"

def test_create_product_invalid_supplier(client,db_session):
    category=Category(
        name="Supplier Test Category",
        description="Testing invalid supplier"
    )
    
    db_session.add(category)
    db_session.flush()
    
    product_data={
        "name":"Invalid Supplier Mouse",
        "price":999,
        "sku":"INVALID-SUP-001",
        "category_id":category.id,
        "supplier_id":99999
    }
    
    response=client.post("/products/",json=product_data)
    
    assert response.status_code==409
    assert response.json()["message"]=="Invalid supplier_id"

def test_create_product_invalid_price(client):
    product_data={
        "name":"Invalid Price Mouse",
        "price":-100,
        "sku":"INVALID-PRICE-001",
        "category_id":1
    }

    response=client.post("/products/",json=product_data)
    
    assert response.status_code== 422
    assert response.json()["message"]=="Validation failed"
    
def test_update_product(client,db_session):
    category=Category(
        name="Update Test Category",
        description="Testing updates"
    )   
    
    db_session.add(category)
    db_session.flush()
    
    product = Product(
        name="Original Mouse",
        price=999,
        sku="UPDATE-001",
        category_id=category.id
    )
    db_session.add(product)
    db_session.flush()
    
    response= client.patch(f"/products/{product.id}",json={"name":"Updated Mouse"})
    
    assert response.status_code==200
    
    data= response.json()
    assert data["name"]=="Updated Mouse"
    assert data["price"]==999
    assert data["sku"]=="UPDATE-001"
    
    
def test_update_product_not_found(client):
    response = client.patch(
        "/products/99999",
        json={"name": "Updated Mouse"}
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Product not found"
    
    
def test_replace_product(client, db_session):
    category = Category(
        name="Replace Test Category",
        description="Testing replacement"
    )
    db_session.add(category)
    db_session.flush()

    product = Product(
        name="Original Mouse",
        price=999,
        sku="REPLACE-001",
        category_id=category.id
    )
    db_session.add(product)
    db_session.flush()

    replacement_data = {
        "name": "Replacement Keyboard",
        "price": 1999,
        "sku": "REPLACE-002",
        "description": "Updated product",
        "category_id": category.id
    }

    response = client.put(
        f"/products/{product.id}",
        json=replacement_data
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Replacement Keyboard"
    assert data["price"] == 1999.00
    assert data["sku"] == "REPLACE-002"
    assert data["description"] == "Updated product"    
    
def test_replace_product_not_found(client):
    replacement_data = {
        "name": "Replacement Mouse",
        "price": 999,
        "sku": "REPLACE-404",
        "category_id": 1
    }

    response = client.put(
        "/products/99999",
        json=replacement_data
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Product not found"    
    
def test_delete_product(client, db_session):
    category = Category(
        name="Delete Test Category",
        description="Testing deletion"
    )
    db_session.add(category)
    db_session.flush()

    product = Product(
        name="Delete Mouse",
        price=999,
        sku="DELETE-001",
        category_id=category.id
    )
    db_session.add(product)
    db_session.flush()

    product_id = product.id

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"

    deleted_product = db_session.query(Product).filter(
        Product.id == product_id
    ).first()

    assert deleted_product is None    
    
    
def test_delete_product_not_found(client):
    response = client.delete("/products/99999")

    assert response.status_code == 404
    assert response.json()["message"] == "Product not found"  
    
def test_delete_products_with_stock(client,db_session):
    category=Category(
        name="Stock Protectoin Category",
        description="Testing FK protection"
    )    
    db_session.add(category)
    db_session.flush()
    
    warehouse=Warehouse(
        name="Test Warehouse",
        location="Test Location"
    )
    db_session.add(warehouse)
    db_session.flush()
    
    product = Product(
        name="Stocked Mouse",
        price=999,
        sku="STOCK-DELETE-001",
        category_id=category.id
    )
    db_session.add(product)
    db_session.flush()
    
    stock = WarehouseStock(
        product_id=product.id,
        warehouse_id=warehouse.id,
        quantity=10
    )
    db_session.add(stock)
    db_session.flush()
    
    response = client.delete(f"/products/{product.id}")

    assert response.status_code == 409
    assert response.json()["message"] == (
        "Cannot delete product because it has associated records"
    )


#SUPPLER ROUTES TESTING
def test_get_suppliers(client):
    response = client.get("/suppliers/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_suppliers_with_data(client, db_session):
    supplier = Supplier(
        name="Test Supplier"
    )

    db_session.add(supplier)
    db_session.flush()

    response = client.get("/suppliers/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Supplier"
  
def test_get_supplier_by_id(client,db_session):
    supplier=Supplier(
        name="Test Supplier"
    )
    
    db_session.add(supplier)
    db_session.flush()
    
    response=client.get(f"/suppliers/{supplier.id}")
    
    assert response.status_code== 200
    data=response.json()
    assert data["name"]=="Test Supplier"
  
def test_get_supplier_not_found(client):
    response=client.get("/suppliers/99999") 
    
    assert response.status_code==404
    assert response.json()["message"]=="Supplier not found"
  
def test_create_supplier(client,db_session):
    supplier_data={
        "name":"New Test Supplier"
    }
    
    response=client.post(
        "/suppliers/",
        json=supplier_data
    )
    
    assert response.status_code == 200
    
    data=response.json()
    
    assert data["name"] == "New Test Supplier"
    
    supplier= db_session.query(Supplier).filter(
        Supplier.name=="New Test Supplier"
    ).first()
    
    assert supplier is not None
  
def test_update_supplier(client,db_session):
    supplier=Supplier(name="Old Supplier")
    db_session.add(supplier)
    db_session.flush()
    
    response=client.patch(
        f"/suppliers/{supplier.id}",
        json={"name": "Updated Supplier"}
    )  
    
    assert response.status_code==200
    assert response.json()["name"]=="Updated Supplier"
    
    db_session.refresh(supplier)
    assert supplier.name=="Updated Supplier"
  
def test_update_supplier_not_found(client):
    response=client.patch(
        "/suppliers/99999",
        json={"name":"Updated Supplier"}
    )  
    
    assert response.status_code==404
    assert response.json()["message"] == "Supplier not found"
  
  
def test_delete_supplier(client, db_session):
    supplier = Supplier(name="Supplier to Delete")
    db_session.add(supplier)
    db_session.flush()

    response = client.delete(f"/suppliers/{supplier.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Supplier deleted successfully"

    deleted_supplier = db_session.query(Supplier).filter(
        Supplier.id == supplier.id
    ).first()

    assert deleted_supplier is None 
  
  
def test_delete_supplier_not_found(client):
    response=client.delete("/suppliers/9999")  
  
    assert response.status_code==404
    assert response.json()["message"]=="Supplier not found"
    
def test_delete_supplier_with_products(client, db_session):
    category = Category(name="Test Category")
    supplier = Supplier(name="Linked Supplier")

    db_session.add_all([category, supplier])
    db_session.flush()

    product = Product(
        name="Test Product",
        price=100,
        sku="TEST-LINK-001",
        category_id=category.id,
        supplier_id=supplier.id
    )

    db_session.add(product)
    db_session.flush()

    response = client.delete(f"/suppliers/{supplier.id}")

    assert response.status_code == 409
    assert response.json()["message"] == (
        "Cannot delete supplier because products are linked to it"
    )

    existing_supplier = db_session.query(Supplier).filter(
        Supplier.id == supplier.id
    ).first()

    assert existing_supplier is not None   
    
    
    
    
    