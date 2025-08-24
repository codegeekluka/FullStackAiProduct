"""
Pytest configuration and shared fixtures for testing
"""
import os
import pytest
import tempfile
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, JSON, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Create a test-specific base for models
TestBase = declarative_base()

# Create simple test models that don't use pgvector
class TestUser(TestBase):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    password_hash = Column(String)
    onboarding_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TestRecipe(TestBase):
    __tablename__ = "recipe"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    user_id = Column(ForeignKey("user.id"))
    description = Column(Text, nullable=True)
    image = Column(String)
    favorite = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    prep_time = Column(String, nullable=True)
    cook_time = Column(String, nullable=True)
    total_time = Column(String, nullable=True)
    # Use JSON instead of Vector for testing
    embedding = Column(JSON, nullable=True)

class TestIngredient(TestBase):
    __tablename__ = "ingredient"
    
    id = Column(Integer, primary_key=True, index=True)
    ingredient = Column(Text)
    recipe_id = Column(ForeignKey("recipe.id"))
    embedding = Column(JSON, nullable=True)

class TestInstruction(TestBase):
    __tablename__ = "instruction"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    step_number = Column(Integer)
    recipe_id = Column(ForeignKey("recipe.id"))
    embedding = Column(JSON, nullable=True)

class TestUserSession(TestBase):
    __tablename__ = "user_session"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey("user.id"))
    recipe_id = Column(ForeignKey("recipe.id"), nullable=True)
    session_type = Column(String, default="cooking")
    status = Column(String, default="active")
    current_step = Column(Integer, default=0)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Test database configuration - using SQLite for simplicity
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing"""
    # Create all tables for SQLite testing
    TestBase.metadata.create_all(bind=engine)
    yield engine
    TestBase.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden dependencies"""
    
    # Mock the database dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Mock the current user dependency
    def override_get_current_user():
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.firstname = "Test"
        mock_user.lastname = "User"
        mock_user.onboarding_complete = True
        return mock_user
    
    # Create a mock app
    mock_app = Mock()
    mock_app.dependency_overrides = {
        'get_db': override_get_db,
        'get_current_user': override_get_current_user
    }
    
    with TestClient(mock_app) as test_client:
        yield test_client


@pytest.fixture
def mock_user() -> Dict[str, Any]:
    """Mock user data for testing"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "firstname": "Test",
        "lastname": "User",
        "onboarding_complete": True,
        "password_hash": "hashed_password"
    }


@pytest.fixture
def sample_recipe_data() -> Dict[str, Any]:
    """Sample recipe data for testing"""
    return {
        "title": "Test Recipe",
        "description": "A delicious test recipe",
        "ingredients": ["Ingredient 1", "Ingredient 2", "Ingredient 3"],
        "instructions": ["Step 1", "Step 2", "Step 3"],
        "prep_time": "15 minutes",
        "cook_time": "30 minutes",
        "total_time": "45 minutes",
        "image": "https://example.com/image.jpg",
        "tags": ["test", "easy"]
    }


@pytest.fixture
def sample_user(db_session) -> TestUser:
    """Create a test user in the database"""
    user = TestUser(
        username="testuser",
        email="test@example.com",
        firstname="Test",
        lastname="User",
        onboarding_complete=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_recipe(db_session, sample_user) -> TestRecipe:
    """Create a test recipe in the database"""
    recipe = TestRecipe(
        title="Test Recipe",
        slug="test-recipe",
        description="A delicious test recipe",
        user_id=sample_user.id,
        image="https://example.com/image.jpg",
        favorite=False,
        is_active=True,
        prep_time="15 minutes",
        cook_time="30 minutes",
        total_time="45 minutes"
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    
    # Add ingredients
    ingredients = [
        TestIngredient(ingredient="Ingredient 1", recipe_id=recipe.id),
        TestIngredient(ingredient="Ingredient 2", recipe_id=recipe.id),
        TestIngredient(ingredient="Ingredient 3", recipe_id=recipe.id)
    ]
    for ingredient in ingredients:
        db_session.add(ingredient)
    
    # Add instructions
    instructions = [
        TestInstruction(description="Step 1", recipe_id=recipe.id, step_number=1),
        TestInstruction(description="Step 2", recipe_id=recipe.id, step_number=2),
        TestInstruction(description="Step 3", recipe_id=recipe.id, step_number=3)
    ]
    for instruction in instructions:
        db_session.add(instruction)
    
    db_session.commit()
    return recipe


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls"""
    with patch('backend.services.ai_assistant.openai') as mock:
        # Mock embeddings
        mock.embeddings.create.return_value.data[0].embedding = [0.1] * 1536
        
        # Mock chat completions
        mock.chat.completions.create.return_value.choices[0].message.content = "Test AI response"
        
        # Mock moderation
        mock.moderations.create.return_value.results[0].flagged = False
        
        yield mock


@pytest.fixture
def mock_elevenlabs():
    """Mock ElevenLabs API calls"""
    with patch('backend.services.tts_service.elevenlabs') as mock:
        mock.generate.return_value = b"fake_audio_data"
        yield mock


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file for testing"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"fake_audio_data")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# Environment variables for testing
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ["ELEVENLABS_API_KEY"] = "test_elevenlabs_key"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["ALGORITHM"] = "HS256"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    yield
    # Clean up environment variables if needed
