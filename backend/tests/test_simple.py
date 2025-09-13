"""
Simple test to verify test configuration works
"""
import pytest
from backend.tests.conftest import TestUser, TestRecipe, TestIngredient, TestInstruction


def test_basic_functionality():
    """Test that basic pytest functionality works"""
    assert True


def test_mock_user_fixture(mock_user):
    """Test that the mock_user fixture works"""
    assert mock_user["username"] == "testuser"
    assert mock_user["email"] == "test@example.com"


def test_sample_recipe_data_fixture(sample_recipe_data):
    """Test that the sample_recipe_data fixture works"""
    assert sample_recipe_data["title"] == "Test Recipe"
    assert len(sample_recipe_data["ingredients"]) == 3


def test_environment_variables():
    """Test that environment variables are set"""
    import os
    assert os.environ.get("OPENAI_API_KEY") == "test_openai_key"
    assert os.environ.get("ELEVENLABS_API_KEY") == "test_elevenlabs_key"
    assert os.environ.get("SECRET_KEY") == "test_secret_key"


def test_database_models(db_session):
    """Test that database models work with SQLite"""
    # Test creating a user
    user = TestUser(
        username="testuser2",
        email="test2@example.com",
        firstname="Test2",
        lastname="User2",
        onboarding_complete=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser2"
    
    # Test creating a recipe
    recipe = TestRecipe(
        title="Test Recipe 2",
        slug="test-recipe-2",
        description="Another test recipe",
        user_id=user.id,
        image="test2.jpg",
        favorite=False,
        is_active=True
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    
    assert recipe.id is not None
    assert recipe.title == "Test Recipe 2"
    assert recipe.user_id == user.id


def test_sample_user_fixture(sample_user):
    """Test that the sample_user fixture works"""
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"
    assert sample_user.id is not None


def test_sample_recipe_fixture(sample_recipe):
    """Test that the sample_recipe fixture works"""
    assert sample_recipe.title == "Test Recipe"
    assert sample_recipe.slug == "test-recipe"
    assert sample_recipe.id is not None
