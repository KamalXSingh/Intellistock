from app.models.category import Category
from app.models.products import Product

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
    
    product = db_session.query(Product).filter(
       Product.sku == "TEST-MOUSE-001"
    ).first()

    assert product is not None
    assert product.name == "Test Mouse"