"""
Unit tests for database models
"""
import pytest
from sqlalchemy.orm import Session
from backend.database.db_models import User, Recipe, Ingredient, Instruction, UserSession, UserConversation


class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, db_session: Session):
        """Test creating a new user"""
        user = User(
            username="testuser",
            email="test@example.com",
            firstname="Test",
            lastname="User",
            onboarding_complete=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.firstname == "Test"
        assert user.lastname == "User"
        assert user.onboarding_complete is True
    
    def test_user_relationships(self, db_session: Session):
        """Test user relationships with recipes"""
        user = User(
            username="testuser",
            email="test@example.com",
            firstname="Test",
            lastname="User"
        )
        db_session.add(user)
        db_session.commit()
        
        recipe = Recipe(
            title="Test Recipe",
            slug="test-recipe",
            description="Test description",
            user_id=user.id,
            image="test.jpg",
            favorite=False,
            is_active=True,
            tags=[]
        )
        db_session.add(recipe)
        db_session.commit()
        
        assert recipe.user_id == user.id
        assert len(user.recipes) == 1
        assert user.recipes[0].title == "Test Recipe"


class TestRecipeModel:
    """Test Recipe model functionality"""
    
    def test_create_recipe(self, db_session: Session, sample_user: User):
        """Test creating a new recipe"""
        recipe = Recipe(
            title="Test Recipe",
            slug="test-recipe",
            description="A delicious test recipe",
            user_id=sample_user.id,
            image="https://example.com/image.jpg",
            favorite=False,
            is_active=True,
            tags=[],
            prep_time="15 minutes",
            cook_time="30 minutes",
            total_time="45 minutes"
        )
        db_session.add(recipe)
        db_session.commit()
        db_session.refresh(recipe)
        
        assert recipe.id is not None
        assert recipe.title == "Test Recipe"
        assert recipe.slug == "test-recipe"
        assert recipe.user_id == sample_user.id
        assert recipe.favorite is False
        assert recipe.is_active is True
    
    def test_recipe_relationships(self, db_session: Session, sample_user: User):
        """Test recipe relationships with ingredients and instructions"""
        recipe = Recipe(
            title="Test Recipe",
            slug="test-recipe",
            description="Test description",
            user_id=sample_user.id,
            image="test.jpg",
            favorite=False,
            is_active=True,
            tags=[]
        )
        db_session.add(recipe)
        db_session.commit()
        
        # Add ingredients
        ingredient1 = Ingredient(ingredient="Salt", recipe_id=recipe.id)
        ingredient2 = Ingredient(ingredient="Pepper", recipe_id=recipe.id)
        db_session.add_all([ingredient1, ingredient2])
        
        # Add instructions
        instruction1 = Instruction(description="Step 1", recipe_id=recipe.id, step_number=1)
        instruction2 = Instruction(description="Step 2", recipe_id=recipe.id, step_number=2)
        db_session.add_all([instruction1, instruction2])
        
        db_session.commit()
        
        assert len(recipe.ingredient_list) == 2
        assert len(recipe.instruction_list) == 2
        assert recipe.ingredient_list[0].ingredient == "Salt"
        assert recipe.instruction_list[0].description == "Step 1"
    
    def test_recipe_to_dict(self, db_session: Session, sample_user: User):
        """Test recipe to_dict method"""
        recipe = Recipe(
            title="Test Recipe",
            slug="test-recipe",
            description="Test description",
            user_id=sample_user.id,
            image="test.jpg",
            favorite=True,
            is_active=True,
            tags=[]
        )
        db_session.add(recipe)
        db_session.commit()
        
        recipe_dict = recipe.to_dict()
        
        assert recipe_dict["title"] == "Test Recipe"
        assert recipe_dict["slug"] == "test-recipe"
        assert recipe_dict["favorite"] is True
        assert recipe_dict["is_active"] is True


class TestIngredientModel:
    """Test Ingredient model functionality"""
    
    def test_create_ingredient(self, db_session: Session, sample_recipe: Recipe):
        """Test creating a new ingredient"""
        ingredient = Ingredient(
            ingredient="Test Ingredient",
            recipe_id=sample_recipe.id
        )
        db_session.add(ingredient)
        db_session.commit()
        db_session.refresh(ingredient)
        
        assert ingredient.id is not None
        assert ingredient.ingredient == "Test Ingredient"
        assert ingredient.recipe_id == sample_recipe.id


class TestInstructionModel:
    """Test Instruction model functionality"""
    
    def test_create_instruction(self, db_session: Session, sample_recipe: Recipe):
        """Test creating a new instruction"""
        instruction = Instruction(
            description="Test instruction",
            recipe_id=sample_recipe.id,
            step_number=1
        )
        db_session.add(instruction)
        db_session.commit()
        db_session.refresh(instruction)
        
        assert instruction.id is not None
        assert instruction.description == "Test instruction"
        assert instruction.recipe_id == sample_recipe.id
        assert instruction.step_number == 1


class TestUserSessionModel:
    """Test UserSession model functionality"""
    
    def test_create_session(self, db_session: Session, sample_user: User, sample_recipe: Recipe):
        """Test creating a new user session"""
        session = UserSession(
            user_id=sample_user.id,
            recipe_id=sample_recipe.id,
            session_id="test-session-123",
            current_step=1,
            is_active=True
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.recipe_id == sample_recipe.id
        assert session.session_id == "test-session-123"
        assert session.current_step == 1
        assert session.is_active is True


class TestUserConversationModel:
    """Test UserConversation model functionality"""
    
    def test_create_conversation(self, db_session: Session):
        """Test creating a new conversation entry"""
        conversation = UserConversation(
            session_id="test-session-123",
            role="user",
            message="Hello, how do I cook this?",
            query_type="general",
            response_time_ms=1500
        )
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.session_id == "test-session-123"
        assert conversation.role == "user"
        assert conversation.message == "Hello, how do I cook this?"
        assert conversation.query_type == "general"
        assert conversation.response_time_ms == 1500
