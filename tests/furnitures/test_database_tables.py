import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from source.services.database import Base
from source.models.Furniture import Furniture, Bed, Chair, Table, BookShelf, Sofa

# Set up a temporary database for testing
@pytest.fixture(scope='module')
def test_engine():
    engine = create_engine('sqlite:///:memory:')  # In-memory database
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='module')
def test_session(test_engine):
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()

def test_table_creation(test_engine):
    inspector = test_engine.dialect.get_inspector(test_engine)
    tables = inspector.get_table_names()
    expected_tables = ['furniture', 'beds', 'chairs', 'tables', 'bookshelves', 'sofas']
    assert all(table in tables for table in expected_tables), "All tables should be created."
