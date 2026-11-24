import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base, get_db
from app.main import app


from fastapi.testclient import TestClient

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not configured")

test_engine = create_engine(TEST_DATABASE_URL)
Base.metadata.create_all(bind=test_engine)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

@pytest.fixture
def db_session():
    connection=test_engine.connect()
    
    transaction=connection.begin()
    
    session=TestingSessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint"
    )
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db]=override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()