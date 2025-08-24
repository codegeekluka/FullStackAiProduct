"""
Unit tests for AI assistant service
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from backend.services.ai_assistant import AIAssistantService
from backend.database.db_models import Recipe, Ingredient, Instruction, UserSession, UserConversation


class TestAIAssistantService:
    """Test AI Assistant Service functionality"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI assistant service instance for testing"""
        with patch('backend.services.ai_assistant.openai') as mock_openai:
            with patch('backend.services.ai_assistant.OpenAIEmbeddings') as mock_embeddings:
                with patch('backend.services.ai_assistant.ChatOpenAI') as mock_chat:
                    # Mock the embeddings model
                    mock_embeddings_instance = Mock()
                    mock_embeddings_instance.embed_query.return_value = [0.1] * 1536
                    mock_embeddings.return_value = mock_embeddings_instance
                    
                    # Mock the chat model
                    mock_chat_instance = Mock()
                    mock_chat.return_value = mock_chat_instance
                    
                    # Mock OpenAI API key
                    mock_openai.api_key = "test_key"
                    
                    service = AIAssistantService()
                    yield service
    
    def test_generate_embeddings(self, ai_service):
        """Test generating embeddings"""
        text = "Test text for embedding"
        embedding = ai_service.generate_embeddings(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
    
    def test_chunk_text(self, ai_service):
        """Test text chunking functionality"""
        text = "This is a long text that should be chunked into smaller pieces for better processing."
        chunks = ai_service.chunk_text(text)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    def test_update_recipe_embeddings(self, ai_service, db_session: Session, sample_user):
        """Test updating recipe embeddings"""
        # Create a test recipe
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
        ingredient = Ingredient(ingredient="Test Ingredient", recipe_id=recipe.id)
        db_session.add(ingredient)
        
        # Add instructions
        instruction = Instruction(description="Test instruction", recipe_id=recipe.id, step_number=1)
        db_session.add(instruction)
        db_session.commit()
        
        # Update embeddings
        ai_service.update_recipe_embeddings(db_session, recipe.id)
        
        # Verify embeddings were created
        db_session.refresh(recipe)
        db_session.refresh(ingredient)
        db_session.refresh(instruction)
        
        assert recipe.embedding is not None
        assert ingredient.embedding is not None
        assert instruction.embedding is not None
    
    def test_hybrid_retrieve(self, ai_service, db_session: Session, sample_user):
        """Test hybrid retrieval functionality"""
        
        # Create a test recipe with embeddings
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
        
        # Add ingredients with embeddings
        ingredient = Ingredient(
            ingredient="Salt",
            recipe_id=recipe.id,
            embedding=np.array([0.1] * 1536)
        )
        db_session.add(ingredient)
        
        # Add instructions with embeddings
        instruction = Instruction(
            description="Add salt to taste",
            recipe_id=recipe.id,
            step_number=1,
            embedding=np.array([0.1] * 1536)
        )
        db_session.add(instruction)
        db_session.commit()
        
        # Test retrieval
        query = "How much salt should I add?"
        results = ai_service.hybrid_retrieve(db_session, recipe.id, query, top_k=5)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(result, dict) for result in results)
        assert all("type" in result for result in results)
        assert all("content" in result for result in results)
        assert all("similarity_score" in result for result in results)
    
    def test_create_cooking_context(self, ai_service, db_session: Session, sample_user):
        """Test creating cooking context"""
        # Create a test recipe
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
        
        # Create mock retrieved chunks
        retrieved_chunks = [
            {
                "type": "ingredient",
                "content": "Salt",
                "id": 1,
                "similarity_score": 0.8
            },
            {
                "type": "instruction",
                "content": "Add salt to taste",
                "step_number": 1,
                "id": 1,
                "similarity_score": 0.9
            }
        ]
        
        context = ai_service.create_cooking_context(db_session, recipe.id, retrieved_chunks)
        
        assert isinstance(context, str)
        assert "Test Recipe" in context
        assert "Salt" in context
        assert "Add salt to taste" in context
    
    def test_get_conversation_history(self, ai_service, db_session: Session):
        """Test getting conversation history"""
        # Create conversation entries
        conversations = [
            UserConversation(
                session_id="test-session",
                role="user",
                message="How do I cook this?",
                query_type="general"
            ),
            UserConversation(
                session_id="test-session",
                role="assistant",
                message="Follow the recipe steps carefully.",
                query_type="ai_response"
            )
        ]
        
        for conv in conversations:
            db_session.add(conv)
        db_session.commit()
        
        history = ai_service.get_conversation_history(db_session, "test-session")
        
        assert isinstance(history, list)
        assert len(history) == 2
        assert all(isinstance(conv, dict) for conv in history)
        assert all("role" in conv for conv in history)
        assert all("message" in conv for conv in history)
    
    def test_generate_ai_response(self, ai_service):
        """Test generating AI response"""
        query = "How do I cook this recipe?"
        context = "Recipe: Test Recipe\nIngredient: Salt\nStep 1: Add salt"
        conversation_history = [
            {"role": "user", "message": "Hello", "timestamp": "2023-01-01"}
        ]
        
        with patch.object(ai_service.chat_model, 'ainvoke') as mock_invoke:
            mock_invoke.return_value.content = "Test AI response"
            
            response = ai_service.generate_ai_response(query, context, conversation_history)
            
            assert isinstance(response, str)
            assert response == "Test AI response"
    
    def test_moderate_content(self, ai_service):
        """Test content moderation"""
        with patch('backend.services.ai_assistant.openai') as mock_openai:
            # Test appropriate content
            mock_openai.moderations.create.return_value.results[0].flagged = False
            result = ai_service.moderate_content("How do I cook this recipe?")
            assert result is True
            
            # Test inappropriate content
            mock_openai.moderations.create.return_value.results[0].flagged = True
            result = ai_service.moderate_content("inappropriate content")
            assert result is False
    
    def test_create_session(self, ai_service, db_session: Session, sample_user, sample_recipe):
        """Test creating a new session"""
        session_id = ai_service.create_session(db_session, sample_user.id, sample_recipe.id)
        
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Verify session was created in database
        session = db_session.query(UserSession).filter(UserSession.session_id == session_id).first()
        assert session is not None
        assert session.user_id == sample_user.id
        assert session.recipe_id == sample_recipe.id
        assert session.is_active is True
        assert session.current_step == 1
    
    def test_log_conversation(self, ai_service, db_session: Session):
        """Test logging conversation"""
        session_id = "test-session"
        role = "user"
        message = "Test message"
        query_type = "general"
        response_time_ms = 1500
        
        ai_service.log_conversation(db_session, session_id, role, message, query_type, response_time_ms)
        
        # Verify conversation was logged
        conversation = db_session.query(UserConversation).filter(
            UserConversation.session_id == session_id
        ).first()
        
        assert conversation is not None
        assert conversation.role == role
        assert conversation.message == message
        assert conversation.query_type == query_type
        assert conversation.response_time_ms == response_time_ms
    
    def test_extract_current_step(self, ai_service):
        """Test extracting current step from AI response"""
        # Test response with step information
        response_with_step = "Now you're on step 3 of the recipe. Continue with the next step."
        current_step = ai_service.extract_current_step(response_with_step, 2)
        assert current_step == 3
        
        # Test response without step information
        response_without_step = "This is a general cooking tip."
        current_step = ai_service.extract_current_step(response_without_step, 2)
        assert current_step == 2  # Should return current step unchanged
    
    def test_calculate_similarity(self, ai_service):
        """Test similarity calculation"""
        embedding1 = np.array([1.0, 0.0, 0.0])
        embedding2 = np.array([1.0, 0.0, 0.0])
        
        similarity = ai_service._calculate_similarity(embedding1, embedding2)
        
        assert isinstance(similarity, float)
        assert similarity == 1.0  # Identical vectors should have similarity 1.0
        
        # Test orthogonal vectors
        embedding3 = np.array([0.0, 1.0, 0.0])
        similarity = ai_service._calculate_similarity(embedding1, embedding3)
        assert similarity == 0.0  # Orthogonal vectors should have similarity 0.0
