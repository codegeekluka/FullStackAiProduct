"""
Integration tests for AI Assistant API endpoints
"""
import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.database.db_models import User, Recipe, UserSession


class TestAIAssistantAPI:
    """Test AI Assistant API endpoints"""
    
    def test_start_cooking_session(self, client: TestClient, sample_recipe: Recipe):
        """Test starting a cooking session"""
        with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
            mock_ai.create_session.return_value = "test-session-123"
            
            response = client.post(
                "/start_session",
                json={"recipe_id": sample_recipe.id}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session-123"
            assert data["recipe_title"] == sample_recipe.title
            assert "Started cooking session" in data["message"]
    
    def test_start_cooking_session_recipe_not_found(self, client: TestClient):
        """Test starting a session with non-existent recipe"""
        response = client.post(
            "/start_session",
            json={"recipe_id": 99999}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"
    
    def test_ask_ai_assistant(self, client: TestClient, sample_recipe: Recipe):
        """Test asking the AI assistant a question"""
        # First create a session
        with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
            mock_ai.create_session.return_value = "test-session-123"
            
            # Mock session retrieval
            mock_session = Mock()
            mock_session.recipe_id = sample_recipe.id
            mock_session.current_step = 1
            mock_session.is_active = True
            
            # Mock AI service methods
            mock_ai.moderate_content.return_value = True
            mock_ai.hybrid_retrieve.return_value = [{"type": "instruction", "content": "Test content"}]
            mock_ai.create_cooking_context.return_value = "Test context"
            mock_ai.get_conversation_history.return_value = []
            mock_ai.generate_ai_response.return_value = "Test AI response"
            mock_ai.extract_current_step.return_value = 1
            
            # Mock TTS service
            with patch('backend.services.tts_service.tts_service') as mock_tts:
                mock_tts.generate_audio_url.return_value = "https://example.com/audio.mp3"
                
                response = client.post(
                    "/ask",
                    json={
                        "session_id": "test-session-123",
                        "message": "How do I cook this recipe?",
                        "query_type": "general"
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["response"] == "Test AI response"
                assert data["session_id"] == "test-session-123"
                assert data["current_step"] == 1
                assert data["audio_url"] == "https://example.com/audio.mp3"
    
    def test_ask_ai_assistant_invalid_session(self, client: TestClient):
        """Test asking AI assistant with invalid session"""
        response = client.post(
            "/ask",
            json={
                "session_id": "invalid-session",
                "message": "How do I cook this recipe?",
                "query_type": "general"
            }
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found or inactive"
    
    def test_ask_ai_assistant_content_moderation_failed(self, client: TestClient, sample_recipe: Recipe):
        """Test asking AI assistant with inappropriate content"""
        with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
            mock_ai.moderate_content.return_value = False
            
            response = client.post(
                "/ask",
                json={
                    "session_id": "test-session-123",
                    "message": "inappropriate content",
                    "query_type": "general"
                }
            )
            
            assert response.status_code == 400
            assert "Content violates community guidelines" in response.json()["detail"]
    
    def test_upload_audio(self, client: TestClient, sample_recipe: Recipe):
        """Test uploading audio for transcription"""
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(b"fake_audio_data")
            temp_path = temp_file.name
        
        try:
            with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
                with patch('backend.Apis.ai_assistant.openai') as mock_openai:
                    # Mock session
                    mock_session = Mock()
                    mock_session.recipe_id = sample_recipe.id
                    mock_session.current_step = 1
                    mock_session.is_active = True
                    
                    # Mock AI service methods
                    mock_ai.moderate_content.return_value = True
                    mock_ai.hybrid_retrieve.return_value = [{"type": "instruction", "content": "Test content"}]
                    mock_ai.create_cooking_context.return_value = "Test context"
                    mock_ai.get_conversation_history.return_value = []
                    mock_ai.generate_ai_response.return_value = "Test AI response"
                    mock_ai.extract_current_step.return_value = 1
                    
                    # Mock OpenAI transcription
                    mock_openai.audio.transcriptions.create.return_value = "Hello, how do I cook this?"
                    
                    # Mock TTS service
                    with patch('backend.services.tts_service.tts_service') as mock_tts:
                        mock_tts.generate_audio_url.return_value = "https://example.com/audio.mp3"
                        
                        with open(temp_path, 'rb') as audio_file:
                            response = client.post(
                                "/upload_audio",
                                data={"session_id": "test-session-123"},
                                files={"audio_file": ("test.wav", audio_file, "audio/wav")}
                            )
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert data["transcribed_text"] == "Hello, how do I cook this?"
                        assert data["response"] == "Test AI response"
                        assert data["audio_url"] == "https://example.com/audio.mp3"
                        assert data["current_step"] == 1
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_upload_audio_invalid_format(self, client: TestClient):
        """Test uploading audio with invalid format"""
        # Create a temporary text file (invalid audio format)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"not audio data")
            temp_path = temp_file.name
        
        try:
            with open(temp_path, 'rb') as text_file:
                response = client.post(
                    "/upload_audio",
                    data={"session_id": "test-session-123"},
                    files={"audio_file": ("test.txt", text_file, "text/plain")}
                )
            
            assert response.status_code == 400
            assert "Unsupported audio format" in response.json()["detail"]
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_generate_tts(self, client: TestClient):
        """Test generating TTS audio"""
        with patch('backend.services.tts_service.tts_service') as mock_tts:
            mock_tts.generate_audio.return_value = b"fake_audio_data"
            
            response = client.post(
                "/tts",
                json={"text": "Hello, this is a test message"}
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/mpeg"
    
    def test_get_tts_stream(self, client: TestClient):
        """Test getting TTS audio stream"""
        with patch('backend.services.tts_service.tts_service') as mock_tts:
            mock_tts.get_cached_audio.return_value = b"fake_audio_data"
            
            response = client.get("/tts/stream/test-response-id")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/mpeg"
    
    def test_get_tts_stream_not_found(self, client: TestClient):
        """Test getting TTS audio stream that doesn't exist"""
        with patch('backend.services.tts_service.tts_service') as mock_tts:
            mock_tts.get_cached_audio.side_effect = Exception("Audio not found")
            
            response = client.get("/tts/stream/non-existent-id")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Audio not found"
    
    def test_get_user_sessions(self, client: TestClient, sample_recipe: Recipe):
        """Test getting user sessions"""
        with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
            # Mock session data
            mock_session = Mock()
            mock_session.session_id = "test-session-123"
            mock_session.recipe_id = sample_recipe.id
            mock_session.current_step = 1
            mock_session.is_active = True
            
            response = client.get("/sessions")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_update_session_step(self, client: TestClient):
        """Test updating session step"""
        with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
            # Mock session
            mock_session = Mock()
            mock_session.is_active = True
            
            response = client.put("/sessions/test-session-123/step?step=3")
            
            assert response.status_code == 200
            assert response.json()["message"] == "Step updated successfully"
    
    def test_update_session_step_not_found(self, client: TestClient):
        """Test updating step for non-existent session"""
        response = client.put("/sessions/non-existent-session/step?step=3")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"
    
    def test_end_session(self, client: TestClient):
        """Test ending a session"""
        with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
            # Mock session
            mock_session = Mock()
            mock_session.is_active = True
            
            response = client.delete("/sessions/test-session-123")
            
            assert response.status_code == 200
            assert response.json()["message"] == "Session ended successfully"
    
    def test_end_session_not_found(self, client: TestClient):
        """Test ending a non-existent session"""
        response = client.delete("/sessions/non-existent-session")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"
    
    def test_cleanup_inactive_sessions(self, client: TestClient):
        """Test cleaning up inactive sessions"""
        with patch('backend.services.ai_assistant.ai_assistant') as mock_ai:
            response = client.post("/cleanup-sessions?hours_inactive=24")
            
            assert response.status_code == 200
            assert "Cleaned up sessions" in response.json()["message"]
            mock_ai.cleanup_inactive_sessions.assert_called_once()
