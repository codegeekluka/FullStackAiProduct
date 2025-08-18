# AI Chef Assistant Setup Guide

This guide will help you set up the AI Chef Assistant feature for your Recipe App.

## Prerequisites

1. **PostgreSQL with pgvector extension**
2. **OpenAI API key**
3. **Redis (optional, for caching)**
4. **Python 3.8+**

## Step 1: Database Setup

### Install pgvector Extension

1. **For Ubuntu/Debian:**
   ```bash
   sudo apt-get install postgresql-14-pgvector
   ```

2. **For macOS (using Homebrew):**
   ```bash
   brew install pgvector
   ```

3. **For Windows:**
   Download from: https://github.com/pgvector/pgvector/releases

### Enable Extension in PostgreSQL

Connect to your PostgreSQL database and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 2: Environment Configuration

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/recipe_app

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# JWT Secret
SECRET_KEY=your_secret_key_here

# CORS Origins
ALLOWED_ORIGINS=http://localhost:5173

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# AI Assistant Configuration
MAX_CONVERSATION_HISTORY=20
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
EMBEDDING_DIMENSIONS=1536

# Session Configuration
SESSION_CLEANUP_HOURS=24
```

## Step 3: Install Dependencies

### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

## Step 4: Database Migration

Run the database migration to add AI assistant tables:

```bash
cd backend
alembic upgrade head
```

This will:
- Add vector columns to existing tables
- Create user_session and user_conversation tables
- Create vector indexes for semantic search

## Step 5: Generate Embeddings for Existing Recipes

If you have existing recipes, you'll need to generate embeddings for them. You can do this by:

1. **Automatically**: The embeddings will be generated when users start cooking sessions
2. **Manually**: Create a script to batch generate embeddings

Example script (`backend/generate_embeddings.py`):
```python
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from database.db_models import Recipe
from services.ai_assistant import ai_assistant

def generate_all_embeddings():
    db = SessionLocal()
    try:
        recipes = db.query(Recipe).all()
        for recipe in recipes:
            print(f"Generating embeddings for recipe: {recipe.title}")
            ai_assistant.update_recipe_embeddings(db, recipe.id)
        print("All embeddings generated successfully!")
    except Exception as e:
        print(f"Error generating embeddings: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_all_embeddings()
```

## Step 6: Start the Application

### Backend
```bash
cd backend
uvicorn backend.Apis.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Step 7: Test the AI Assistant

1. Navigate to any recipe page
2. Look for the floating "AI Chef" button (bottom right)
3. Click to open the AI assistant
4. Ask questions about the recipe

## Features

### Text Input
- Type questions in the text area
- Press Enter or click the send button
- AI will respond with cooking advice

### Voice Input
- Click the microphone button to start recording
- Speak your question
- Click again to stop recording
- AI will transcribe and respond

### Session Management
- Each cooking session is tracked
- Conversation history is maintained
- Current cooking step can be updated
- Sessions are automatically cleaned up after inactivity

### Smart Retrieval
- Hybrid search combines structured and semantic search
- Retrieves relevant recipe context for each question
- Uses OpenAI embeddings for semantic similarity

## API Endpoints

### AI Assistant Endpoints
- `POST /ai/start_session` - Start a cooking session
- `POST /ai/ask` - Ask the AI assistant a question
- `POST /ai/upload_audio` - Process voice input
- `GET /ai/sessions` - Get user's active sessions
- `PUT /ai/sessions/{session_id}/step` - Update current step
- `DELETE /ai/sessions/{session_id}` - End a session

### Updated Recipe Endpoints
- All recipe creation/update endpoints now automatically generate embeddings
- Embeddings are updated when recipes are modified

## Configuration Options

### Embedding Model
- Model: `text-embedding-3-small`
- Dimensions: 1536
- Can be changed in `backend/services/ai_assistant.py`

### Chat Model
- Model: `gpt-4o-mini`
- Temperature: 0.7
- Max tokens: 1000

### Retrieval Settings
- Top-k chunks: 8 (4 ingredients + 4 instructions)
- Chunk size: 200 characters
- Chunk overlap: 20 characters

### Session Settings
- Max conversation history: 20 messages
- Session cleanup: 24 hours of inactivity
- Auto-cleanup: Enabled

## Troubleshooting

### Common Issues

1. **pgvector extension not found**
   - Ensure pgvector is installed and enabled
   - Check PostgreSQL version compatibility

2. **OpenAI API errors**
   - Verify API key is correct
   - Check API quota and billing

3. **Audio recording not working**
   - Ensure microphone permissions are granted
   - Check browser compatibility

4. **Embeddings not generating**
   - Check OpenAI API key
   - Verify database connection
   - Check for recipe data

### Debug Mode

Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

1. **Caching**: Enable Redis for response caching
2. **Batch Processing**: Generate embeddings in batches
3. **Index Optimization**: Monitor vector index performance

## Security Considerations

1. **Content Moderation**: All user input is checked with OpenAI's moderation API
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Session Isolation**: Each user's sessions are isolated
4. **Data Privacy**: Conversation logs are stored for debugging only

## Monitoring

### Key Metrics to Monitor
- Response times
- Embedding generation success rate
- Session duration
- User engagement
- Error rates

### Logs
- Check application logs for errors
- Monitor OpenAI API usage
- Track database performance

## Future Enhancements

1. **Multi-language Support**: Add support for different languages
2. **Recipe Recommendations**: Suggest similar recipes
3. **Cooking Tips**: Provide general cooking advice
4. **Nutritional Information**: Add nutritional analysis
5. **Recipe Scaling**: Help users scale recipes up/down
6. **Ingredient Substitutions**: Suggest ingredient alternatives

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Verify configuration settings
4. Test with a simple recipe first
