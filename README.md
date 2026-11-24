# IntelliStock — Intelligent Inventory Management System

IntelliStock is a backend-driven inventory management system designed to help businesses manage products, warehouses, stock movements, and inventory levels efficiently.

The project focuses on building a reliable inventory backend with transaction handling, database integrity, stock tracking, and automated testing. Future development will introduce demand forecasting and intelligent inventory recommendations.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM and database operations |
| Pydantic | Request validation and response schemas |
| Alembic | Database migrations |
| Pytest | Automated testing |

## Implemented Features

### 1. Product Management
- Create, retrieve, update, and delete products.
- Manage product details such as name, SKU, price, and description.
- Associate products with categories and suppliers.
- Validate database relationships and prevent invalid deletions.

### 2. Category and Supplier Management
- CRUD operations for product categories.
- CRUD operations for suppliers.
- Relationship management between products, categories, and suppliers.

### 3. Warehouse Management
- Create and manage multiple warehouses.
- Track warehouse locations and active status.
- Maintain separate inventory records for each product in each warehouse.

### 4. Inventory Management
- Stock-in operations to increase inventory.
- Stock-out operations to decrease inventory.
- Stock transfers between warehouses.
- Validation to prevent negative inventory.
- Configurable reorder levels for products in individual warehouses.

### 5. Stock Movement History
- Record stock-in, stock-out, and transfer operations.
- Maintain a history of inventory movements.
- Filter movements by product, warehouse, and movement type.
- Support pagination for movement records.

### 6. Inventory Monitoring
- Identify products with low stock.
- Calculate suggested reorder quantities.
- Identify out-of-stock inventory.
- Generate inventory summary statistics.

### 7. Backend Engineering
- Database transactions and rollback handling.
- Row-level locking for concurrent stock operations.
- Database constraints for data integrity.
- Centralized exception handling.
- Application logging.
- Database schema versioning with Alembic.

### 8. Automated Testing
- Pytest integration.
- FastAPI TestClient.
- Separate test database configuration.
- Dependency overrides for database isolation.
- Transaction rollback between tests.

## Project Structure

```text
IntelliStock/
│
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── core/
│   │   ├── database/
│   │   ├── exceptions/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_main.py
│   │
│   ├── .gitignore
│   ├── alembic.ini
│   └── requirements.txt
│
└── postgressScripts/
    ├── createTable.sql
    ├── insertIntoTable.sql
    └── ...
```

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.12+
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd IntelliStock
```

### 2. Navigate to the Backend

```bash
cd backend
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file inside the `backend/` directory.

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/intellistock_db

TEST_DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/intellistock_test
```

Replace the placeholders with your local PostgreSQL credentials and database names.

**Important:** Never commit your `.env` file or expose database credentials.

Create the required PostgreSQL databases before starting the application.

### 6. Run Database Migrations

```bash
alembic upgrade head
```

This applies the existing Alembic migrations and creates the database schema.

### 7. Start the Backend Server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

### 8. Explore the API

FastAPI provides interactive API documentation through Swagger UI.

`http://127.0.0.1:8000/docs`

You can explore and test the available endpoints directly from your browser.

## Running Tests

Make sure your test database is configured in `.env`.

From the `backend/` directory, run:

```bash
python -m pytest -v
```

Tests use a separate database to avoid modifying development data.

## Future Development

The following capabilities are planned:

- Purchase order and sales order management.
- JWT authentication and role-based access control.
- Advanced automated test coverage.
- Redis caching and Celery background processing.
- Real-time inventory notifications.
- Machine learning-based demand forecasting.
- Stockout and overstock risk prediction.
- Intelligent reorder recommendations.
- Angular frontend integration.
- Docker containerization and AWS deployment.

## Development Approach

IntelliStock is being developed incrementally, with an emphasis on understanding backend engineering concepts and implementing them through practical development.

The project follows a modular monolith architecture, keeping related business functionality organized within a single backend application.

---

**Project Status:** Active Development

**Focus:** Backend Engineering, Inventory Management, Database Design, and Applied Machine Learning