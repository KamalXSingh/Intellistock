from app.models.category import Category
from app.models.products import Product
from app.models.warehouse import Warehouse
from app.models.warehouse_stock import WarehouseStock
from app.models.suppliers import Supplier
from app.models.stock_movement import StockMovement

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
    assert isinstance(response.json()["data"],list)

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
    data=response.json()["data"]
    
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

    data = response.json()["data"]

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
    print(response.json())

    data=response.json()["data"]
    
    assert response.status_code == 200
    assert data["name"] == "Test Mouse"
    assert data["sku"] == "TEST-MOUSE-001"
    assert data["price"]==999
    assert data["category"]["name"]=="Test Electronics"
    
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
    
    data= response.json()["data"]
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

    data = response.json()["data"]
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
    assert isinstance(response.json()["data"], list)

def test_get_suppliers_with_data(client, db_session):
    supplier = Supplier(
        name="Test Supplier"
    )

    db_session.add(supplier)
    db_session.flush()

    response = client.get("/suppliers/")

    assert response.status_code == 200

    data = response.json()["data"]

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
    data=response.json()["data"]
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
    
    data=response.json()["data"]
    
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
    assert response.json()["data"]["name"]=="Updated Supplier"
    
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
    
    
def test_get_categories(client):
    response = client.get("/categories/")

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_get_categories_with_data(client, db_session):
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.flush()

    response = client.get("/categories/")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["name"] == "Electronics"
    
def test_get_category_by_id(client, db_session):
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.flush()

    response = client.get(f"/categories/{category.id}")

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Electronics"


def test_get_category_not_found(client):
    response = client.get("/categories/99999")

    assert response.status_code == 404
    assert response.json()["message"] == "Category not found"    
    
def test_create_category(client, db_session):
    category_data = {
        "name": "Electronics",
        "description": "Electronic products"
    }

    response = client.post("/categories/", json=category_data)

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Electronics"
    assert response.json()["data"]["description"] == "Electronic products"

    category = db_session.query(Category).filter(
        Category.name == "Electronics"
    ).first()

    assert category is not None


def test_create_duplicate_category(client, db_session):
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.flush()

    response = client.post(
        "/categories/",
        json={"name": "Electronics"}
    )

    assert response.status_code == 409
    assert response.json()["message"] == "Category already exists"


def test_create_category_invalid_name(client):
    response = client.post(
        "/categories/",
        json={"name": "A"}
    )

    assert response.status_code == 422        


def test_update_category(client, db_session):
    category = Category(name="Old Category")
    db_session.add(category)
    db_session.flush()

    response = client.patch(
        f"/categories/{category.id}",
        json={"name": "Updated Category"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Updated Category"

    db_session.refresh(category)
    assert category.name == "Updated Category"


def test_update_category_not_found(client):
    response = client.patch(
        "/categories/99999",
        json={"name": "Updated Category"}
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Category not found"


def test_update_category_duplicate_name(client, db_session):
    category1 = Category(name="Electronics")
    category2 = Category(name="Furniture")

    db_session.add_all([category1, category2])
    db_session.flush()

    response = client.patch(
        f"/categories/{category2.id}",
        json={"name": "Electronics"}
    )

    assert response.status_code == 409
    assert response.json()["message"] == "Category name already exists"
    
def test_delete_category(client, db_session):
    category = Category(name="Temporary Category")
    db_session.add(category)
    db_session.flush()

    response = client.delete(f"/categories/{category.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted successfully"

    deleted_category = db_session.query(Category).filter(
        Category.id == category.id
    ).first()

    assert deleted_category is None


def test_delete_category_not_found(client):
    response = client.delete("/categories/99999")

    assert response.status_code == 404
    assert response.json()["message"] == "Category not found"


def test_delete_category_with_products(client, db_session):
    category = Category(name="Linked Category")
    db_session.add(category)
    db_session.flush()

    product = Product(
        name="Test Product",
        price=100,
        sku="CATEGORY-LINK-001",
        category_id=category.id
    )

    db_session.add(product)
    db_session.flush()

    response = client.delete(f"/categories/{category.id}")

    assert response.status_code == 409
    assert response.json()["message"] == (
        "Cannot delete category because products are assigned to it"
    )

    existing_category = db_session.query(Category).filter(
        Category.id == category.id
    ).first()

    assert existing_category is not None    

def test_get_warehouses(client):
    response = client.get("/warehouses/")

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_get_warehouses_with_data(client, db_session):
    warehouse = Warehouse(
        name="Test Warehouse",
        location="Delhi"
    )
    db_session.add(warehouse)
    db_session.flush()

    response = client.get("/warehouses/")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["name"] == "Test Warehouse"


def test_get_warehouse_by_id(client, db_session):
    warehouse = Warehouse(
        name="Test Warehouse",
        location="Delhi"
    )
    db_session.add(warehouse)
    db_session.flush()

    response = client.get(f"/warehouses/{warehouse.id}")

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Test Warehouse"
    assert response.json()["data"]["location"] == "Delhi"


def test_get_warehouse_not_found(client):
    response = client.get("/warehouses/99999")

    assert response.status_code == 404
    assert response.json()["message"] == "Warehouse Not Found"

def test_create_warehouse(client, db_session):
    warehouse_data = {
        "name": "New Warehouse",
        "location": "Mumbai"
    }

    response = client.post("/warehouses/", json=warehouse_data)

    assert response.status_code == 201
    assert response.json()["data"]["name"] == "New Warehouse"
    assert response.json()["data"]["location"] == "Mumbai"
    assert response.json()["data"]["is_active"] is True

    warehouse = db_session.query(Warehouse).filter(
        Warehouse.name == "New Warehouse"
    ).first()

    assert warehouse is not None


def test_create_duplicate_warehouse(client, db_session):
    warehouse = Warehouse(
        name="Existing Warehouse",
        location="Delhi"
    )
    db_session.add(warehouse)
    db_session.flush()

    response = client.post(
        "/warehouses/",
        json={
            "name": "Existing Warehouse",
            "location": "Mumbai"
        }
    )

    assert response.status_code == 409
    assert response.json()["message"] == (
        "Warehouse with the name already exists"
    )


def test_create_warehouse_invalid_data(client):
    response = client.post(
        "/warehouses/",
        json={
            "name": "A",
            "location": "Delhi"
        }
    )

    assert response.status_code == 422

def test_update_warehouse(client, db_session):
    warehouse = Warehouse(
        name="Old Warehouse",
        location="Delhi"
    )
    db_session.add(warehouse)
    db_session.flush()

    response = client.patch(
        f"/warehouses/{warehouse.id}",
        json={"name": "Updated Warehouse"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Updated Warehouse"

    db_session.refresh(warehouse)
    assert warehouse.name == "Updated Warehouse"


def test_update_warehouse_not_found(client):
    response = client.patch(
        "/warehouses/99999",
        json={"name": "Updated Warehouse"}
    )

    assert response.status_code == 404
    assert response.json()["message"] == "Warehouse not found"


def test_update_warehouse_duplicate_name(client, db_session):
    warehouse1 = Warehouse(
        name="Warehouse One",
        location="Delhi"
    )
    warehouse2 = Warehouse(
        name="Warehouse Two",
        location="Mumbai"
    )

    db_session.add_all([warehouse1, warehouse2])
    db_session.flush()

    response = client.patch(
        f"/warehouses/{warehouse2.id}",
        json={"name": "Warehouse One"}
    )

    assert response.status_code == 409
    assert response.json()["message"] == (
        "Warehouse with this name already exists"
    )

def test_delete_warehouse(client, db_session):
    warehouse = Warehouse(
        name="Warehouse to Delete",
        location="Delhi"
    )
    db_session.add(warehouse)
    db_session.flush()

    response = client.delete(f"/warehouses/{warehouse.id}")

    assert response.status_code == 202
    assert response.json()["message"] == "Warehouse deleted successfully"

    deleted_warehouse = db_session.query(Warehouse).filter(
        Warehouse.id == warehouse.id
    ).first()

    assert deleted_warehouse is None


def test_delete_warehouse_not_found(client):
    response = client.delete("/warehouses/99999")

    assert response.status_code == 404
    assert response.json()["message"] == "Warehouse not found"


def test_delete_warehouse_with_stock(client, db_session):
    category = Category(name="Warehouse Test Category")
    warehouse = Warehouse(
        name="Warehouse With Stock",
        location="Delhi"
    )

    db_session.add_all([category, warehouse])
    db_session.flush()

    product = Product(
        name="Warehouse Test Product",
        price=100,
        sku="WAREHOUSE-TEST-001",
        category_id=category.id
    )

    db_session.add(product)
    db_session.flush()

    stock = WarehouseStock(
        product_id=product.id,
        warehouse_id=warehouse.id,
        quantity=20,
        reorder_level=10
    )

    db_session.add(stock)
    db_session.flush()

    response = client.delete(f"/warehouses/{warehouse.id}")

    assert response.status_code == 409
    assert response.json()["message"] == (
        "Cannot delete warehouse because it has stock records"
    )

    existing_warehouse = db_session.query(Warehouse).filter(
        Warehouse.id == warehouse.id
    ).first()

    assert existing_warehouse is not None

#WAREHOUSE STOCKS

def create_stock_test_data(db_session):
    category = Category(name="Stock Test Category")
    warehouse1 = Warehouse(
        name="Stock Test Warehouse 1",
        location="Delhi"
    )
    warehouse2 = Warehouse(
        name="Stock Test Warehouse 2",
        location="Mumbai"
    )

    db_session.add_all([category, warehouse1, warehouse2])
    db_session.flush()

    product = Product(
        name="Stock Test Product",
        price=500,
        sku="STOCK-TEST-001",
        category_id=category.id
    )

    db_session.add(product)
    db_session.flush()

    return product, warehouse1, warehouse2


def create_stock_record(
    db_session,
    product_id,
    warehouse_id,
    quantity=50,
    reorder_level=10
):
    stock = WarehouseStock(
        product_id=product_id,
        warehouse_id=warehouse_id,
        quantity=quantity,
        reorder_level=reorder_level
    )

    db_session.add(stock)
    db_session.flush()

    return stock

def test_get_stock_empty(client):
    response = client.get("/stock/")

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_get_stock_with_data(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(
        db_session,
        product.id,
        warehouse1.id,
        quantity=50
    )

    response = client.get("/stock/")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["quantity"] == 50


def test_get_stock_by_warehouse(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 20)
    create_stock_record(db_session, product.id, warehouse2.id, 40)

    response = client.get(f"/stock/?warehouse_id={warehouse1.id}")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["warehouse_id"] == warehouse1.id


def test_get_stock_by_product(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 20)

    response = client.get(f"/stock/?product_id={product.id}")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["product_id"] == product.id
    
def test_stock_in_new_record(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/in", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 50
    })

    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 50

    stock = db_session.query(WarehouseStock).first()

    assert stock.quantity == 50
    assert stock.reorder_level == 10


def test_stock_in_existing_record(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 50)

    response = client.post("/stock/in", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 20
    })

    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 70


def test_stock_in_custom_reorder_level(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/in", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 50,
        "reorder_level": 25
    })

    assert response.status_code == 200

    stock = db_session.query(WarehouseStock).first()
    assert stock.reorder_level == 25


def test_stock_in_invalid_product(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/in", json={
        "product_id": 99999,
        "warehouse_id": warehouse1.id,
        "quantity": 50
    })

    assert response.status_code == 404


def test_stock_in_invalid_warehouse(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/in", json={
        "product_id": product.id,
        "warehouse_id": 99999,
        "quantity": 50
    })

    assert response.status_code == 404


def test_stock_in_invalid_quantity(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/in", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 0
    })

    assert response.status_code == 422


def test_stock_in_creates_movement(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/in", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 30
    })

    assert response.status_code == 200

    movement = db_session.query(StockMovement).first()

    assert movement is not None
    assert movement.movement_type == "STOCK_IN"
    assert movement.quantity == 30
    
def test_stock_out_success(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 50)

    response = client.post("/stock/out", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 20
    })

    assert response.status_code == 200
    assert response.json()["data"]["quantity"] == 30


def test_stock_out_insufficient_stock(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 10)

    response = client.post("/stock/out", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 20
    })

    assert response.status_code == 409
    assert response.json()["message"] == "Insufficient stock"


def test_stock_out_missing_stock_record(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/out", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 10
    })

    assert response.status_code == 404


def test_stock_out_invalid_product(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/out", json={
        "product_id": 99999,
        "warehouse_id": warehouse1.id,
        "quantity": 10
    })

    assert response.status_code == 404


def test_stock_out_invalid_warehouse(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/out", json={
        "product_id": product.id,
        "warehouse_id": 99999,
        "quantity": 10
    })

    assert response.status_code == 404


def test_stock_out_creates_movement(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 50)

    response = client.post("/stock/out", json={
        "product_id": product.id,
        "warehouse_id": warehouse1.id,
        "quantity": 10
    })

    assert response.status_code == 200

    movement = db_session.query(StockMovement).first()

    assert movement.movement_type == "STOCK_OUT"
    assert movement.quantity == 10
    
def test_stock_transfer_success(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 100)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": warehouse2.id,
        "quantity": 30
    })

    assert response.status_code == 200
    assert response.json()["data"]["source_remaining"] == 70
    assert response.json()["data"]["destination_total"] == 30


def test_stock_transfer_existing_destination(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 100)
    create_stock_record(db_session, product.id, warehouse2.id, 20)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": warehouse2.id,
        "quantity": 30
    })

    assert response.status_code == 200
    assert response.json()["data"]["source_remaining"] == 70
    assert response.json()["data"]["destination_total"] == 50


def test_stock_transfer_same_warehouse(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": warehouse1.id,
        "quantity": 10
    })

    assert response.status_code == 400


def test_stock_transfer_insufficient_stock(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 10)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": warehouse2.id,
        "quantity": 20
    })

    assert response.status_code == 409


def test_stock_transfer_missing_source_stock(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": warehouse2.id,
        "quantity": 10
    })

    assert response.status_code == 404


def test_stock_transfer_invalid_product(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/transfer", json={
        "product_id": 99999,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": warehouse2.id,
        "quantity": 10
    })

    assert response.status_code == 404


def test_stock_transfer_invalid_source_warehouse(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": 99999,
        "destination_warehouse_id": warehouse2.id,
        "quantity": 10
    })

    assert response.status_code == 404


def test_stock_transfer_invalid_destination_warehouse(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": 99999,
        "quantity": 10
    })

    assert response.status_code == 404


def test_stock_transfer_creates_two_movements(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 100)

    response = client.post("/stock/transfer", json={
        "product_id": product.id,
        "source_warehouse_id": warehouse1.id,
        "destination_warehouse_id": warehouse2.id,
        "quantity": 30
    })

    assert response.status_code == 200

    movements = db_session.query(StockMovement).all()

    assert len(movements) == 2
    assert {m.movement_type for m in movements} == {
        "TRANSFER_IN",
        "TRANSFER_OUT"
    }
    

def test_update_reorder_level(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id, 50, 10)

    response = client.patch(
        f"/stock/{product.id}/{warehouse1.id}/reorder-level",
        json={"reorder_level": 25}
    )

    assert response.status_code == 200
    assert response.json()["data"]["reorder_level"] == 25


def test_update_reorder_level_zero(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(db_session, product.id, warehouse1.id)

    response = client.patch(
        f"/stock/{product.id}/{warehouse1.id}/reorder-level",
        json={"reorder_level": 0}
    )

    assert response.status_code == 200
    assert response.json()["data"]["reorder_level"] == 0


def test_update_reorder_level_missing_stock(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.patch(
        f"/stock/{product.id}/{warehouse1.id}/reorder-level",
        json={"reorder_level": 20}
    )

    assert response.status_code == 404


def test_update_reorder_level_negative(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    response = client.patch(
        f"/stock/{product.id}/{warehouse1.id}/reorder-level",
        json={"reorder_level": -5}
    )

    assert response.status_code == 422

def test_get_low_stock(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(
        db_session,
        product.id,
        warehouse1.id,
        quantity=5,
        reorder_level=10
    )

    response = client.get("/stock/low-stock")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1

    result = response.json()["data"][0]

    assert result["quantity"] == 5
    assert result["reorder_level"] == 10
    assert result["reorder_quantity"] == 5


def test_low_stock_excludes_normal_stock(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(
        db_session,
        product.id,
        warehouse1.id,
        quantity=50,
        reorder_level=10
    )

    response = client.get("/stock/low-stock")

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_low_stock_includes_out_of_stock(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(
        db_session,
        product.id,
        warehouse1.id,
        quantity=0,
        reorder_level=10
    )

    response = client.get("/stock/low-stock")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["quantity"] == 0
    
def test_get_movements_empty(client):
    response = client.get("/stock/movements")

    assert response.status_code == 200
    assert response.json()["data"]["total_records"] == 0
    assert response.json()["data"]["movements"] == []


def test_get_movements_with_data(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    db_session.add_all([
        StockMovement(
            product_id=product.id,
            warehouse_id=warehouse1.id,
            movement_type="STOCK_IN",
            quantity=50
        ),
        StockMovement(
            product_id=product.id,
            warehouse_id=warehouse1.id,
            movement_type="STOCK_OUT",
            quantity=10
        )
    ])
    db_session.flush()

    response = client.get("/stock/movements")

    assert response.status_code == 200
    assert response.json()["data"]["total_records"] == 2
    assert len(response.json()["data"]["movements"]) == 2


def test_get_movements_by_product(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    db_session.add(
        StockMovement(
            product_id=product.id,
            warehouse_id=warehouse1.id,
            movement_type="STOCK_IN",
            quantity=50
        )
    )
    db_session.flush()

    response = client.get(
        f"/stock/movements?product_id={product.id}"
    )

    assert response.status_code == 200
    assert response.json()["data"]["total_records"] == 1


def test_get_movements_by_warehouse(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    db_session.add(
        StockMovement(
            product_id=product.id,
            warehouse_id=warehouse2.id,
            movement_type="STOCK_IN",
            quantity=50
        )
    )
    db_session.flush()

    response = client.get(
        f"/stock/movements?warehouse_id={warehouse2.id}"
    )

    assert response.status_code == 200
    assert response.json()["data"]["total_records"] == 1


def test_get_movements_by_type(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    db_session.add_all([
        StockMovement(
            product_id=product.id,
            warehouse_id=warehouse1.id,
            movement_type="STOCK_IN",
            quantity=50
        ),
        StockMovement(
            product_id=product.id,
            warehouse_id=warehouse1.id,
            movement_type="STOCK_OUT",
            quantity=10
        )
    ])
    db_session.flush()

    response = client.get(
        "/stock/movements?movement_type=STOCK_IN"
    )

    assert response.status_code == 200
    assert response.json()["data"]["total_records"] == 1
    assert response.json()["data"]["movements"][0]["movement_type"] == "STOCK_IN"


def test_get_movements_pagination(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    for quantity in [10, 20, 30]:
        db_session.add(
            StockMovement(
                product_id=product.id,
                warehouse_id=warehouse1.id,
                movement_type="STOCK_IN",
                quantity=quantity
            )
        )

    db_session.flush()

    response = client.get("/stock/movements?skip=0&limit=2")

    assert response.status_code == 200
    assert response.json()["data"]["total_records"] == 3
    assert len(response.json()["data"]["movements"]) == 2
    

def test_stock_summary_empty(client):
    response = client.get("/stock/summary")

    assert response.status_code == 200
    assert response.json()["data"]["total_products"] == 0
    assert response.json()["data"]["total_units"] == 0
    assert response.json()["data"]["low_stock_count"] == 0
    assert response.json()["data"]["out_of_stock_count"] == 0


def test_stock_summary_with_data(client, db_session):
    product, warehouse1, warehouse2 = create_stock_test_data(db_session)

    create_stock_record(
        db_session,
        product.id,
        warehouse1.id,
        quantity=5,
        reorder_level=10
    )

    create_stock_record(
        db_session,
        product.id,
        warehouse2.id,
        quantity=0,
        reorder_level=10
    )

    response = client.get("/stock/summary")

    assert response.status_code == 200

    result = response.json()["data"]

    assert result["total_products"] == 1
    assert result["total_units"] == 5
    assert result["low_stock_count"] == 2
    assert result["out_of_stock_count"] == 1
    assert result["active_warehouses"] == 2
    



    