# Recipe App Load Testing Guide

This guide explains how to run comprehensive load tests on your Recipe App using Locust.

## 🎯 What's Being Tested

The load test simulates realistic user behavior including:

### 🔐 Authentication
- User registration and login
- Token verification
- Session management

### 📖 Recipe Management
- Browsing user recipes
- Viewing recipe details
- Creating recipes manually
- Managing favorites and tags
- Setting active recipes
- **Note**: Recipe import from URLs (web scraping) is excluded from testing to avoid external site issues

### 🤖 AI Assistant Usage
- Starting cooking sessions
- Session management and tracking
- Step updates and progress tracking
- Session cleanup
- **Note**: All paid service endpoints are excluded from testing:
  - ❌ `/ai/ask` - OpenAI GPT-4o-mini (conversation)
  - ❌ `/ai/upload_audio` - OpenAI Whisper (audio transcription)
  - ❌ `/ai/tts` - ElevenLabs (text-to-speech)
  - ❌ `/ai/tts/stream/{id}` - ElevenLabs (cached TTS)
  - ❌ `/RecipePage` - Web scraping (external site issues)

### 👤 User Profile Management
- Viewing and updating profiles
- Managing user preferences
- Creating custom tags
- Onboarding data

## 🚀 Quick Start

### Prerequisites

1. **Install Locust**:
   ```bash
   pip install locust
   ```

2. **Start your FastAPI backend**:
   ```bash
   cd backend
   uvicorn backend.Apis.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Ensure your database is running** (PostgreSQL with pgvector)

### Running the Load Test

#### Option 1: Automated Test (Recommended)
```bash
python run_load_test.py
```

This runs a 5-minute test with:
- 50 concurrent users
- 10 users spawned per second
- Generates HTML and CSV reports

#### Option 2: Interactive Mode
```bash
python run_load_test.py interactive
```

This opens Locust's web interface at `http://localhost:8089` where you can:
- Configure test parameters
- Monitor real-time metrics
- Start/stop tests manually

#### Option 3: Direct Locust Command
```bash
locust --host http://localhost:8000
```

## 📊 Test Configuration

### Default Settings
- **Target Host**: `http://localhost:8000`
- **Users**: 50 (medium load)
- **Spawn Rate**: 10 users/second
- **Duration**: 5 minutes
- **Think Time**: 2-8 seconds between actions

### User Types

The test includes three types of simulated users:

1. **RecipeAppUser** (Main user type)
   - Balanced usage of all features
   - Realistic think times
   - Most common user behavior

2. **AIHeavyUser** (AI session management-focused)
   - Intensive AI session management
   - Multiple session operations
   - Step tracking and updates
   - **No paid services used** (OpenAI, ElevenLabs, Whisper, etc.)

3. **RecipeManagerUser** (Recipe-focused)
   - Heavy recipe management
   - Creates multiple recipes
   - Updates existing recipes

## 📈 Understanding Results

### Key Metrics to Monitor

1. **Response Times**
   - Average response time
   - 95th percentile response time
   - Maximum response time

2. **Request Rates**
   - Requests per second
   - Failed requests
   - Success rate

3. **User Behavior**
   - Active users
   - User spawn rate
   - Session duration

### Expected Performance

For a well-optimized system, you should see:
- Average response time: < 500ms
- 95th percentile: < 1s
- Success rate: > 99%
- No timeout errors

## 🔧 Customization

### Modifying Test Scenarios

Edit `locustfile.py` to customize:

1. **User Behavior**:
   ```python
   # Change task weights
   @task(3)  # Higher number = more frequent
   def browse_recipes(self):
       # ...
   ```

2. **Test Data**:
   ```python
   # Add more sample recipes
   sample_recipes = [
       # Add your recipes here
   ]
   ```

3. **Load Parameters**:
   ```python
   # Adjust think time
   wait_time = between(1, 5)  # Faster interactions
   ```

### Adding New Test Scenarios

1. **New User Type**:
   ```python
   class CustomUser(RecipeAppUser):
       @task(2)
       def custom_action(self):
           # Your custom test logic
   ```

2. **New API Endpoint**:
   ```python
   @task(1)
   def test_new_endpoint(self):
       self.client.get("/your/new/endpoint")
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Backend Not Running**
   ```
   ❌ Backend is not running or not accessible
   ```
   **Solution**: Start your FastAPI backend first

2. **Database Connection Issues**
   ```
   ❌ Database connection failed
   ```
   **Solution**: Check PostgreSQL is running and accessible

3. **Authentication Failures**
   ```
   ❌ Login failed for testuser1
   ```
   **Solution**: Check JWT configuration and database setup

4. **400 Bad Request Errors**
   ```
   ❌ 400 Bad Request for url: /register
   ❌ 400 Bad Request for url: /recipe/manualRecipe
   ```
   **Causes**:
   - `/register`: User already exists (expected behavior)
   - `/recipe/manualRecipe`: Invalid recipe data or slug conflicts
   **Solution**: Check backend logs for specific error details

5. **500 Server Errors**
   ```
   ❌ 500 Internal Server Error
   ```
   **Causes**:
   - Database connection pool exhaustion
   - Server resource constraints
   - Database constraint violations
   **Solution**: Reduce concurrent users or check database connection

6. **AI Assistant Not Working**
   ```
   ❌ AI session creation failed
   ```
   **Solution**: Verify OpenAI API key and embeddings setup (note: all paid service endpoints are excluded from testing to avoid costs)

### Debug Mode

Run with verbose logging:
```bash
locust --host http://localhost:8000 --loglevel DEBUG
```

## 📋 Test Data

### Pre-created Test Users
- `testuser1` / `testpass123`
- `testuser2` / `testpass123`
- `testuser3` / `testpass123`
- `testuser4` / `testpass123`
- `testuser5` / `testpass123`

### Sample Recipes
The test includes sample recipes for:
- Classic Spaghetti Carbonara
- Chicken Stir Fry
- Chocolate Chip Cookies

### Excluded Features
- **Web scraping**: Recipe import from URLs (causes 400 errors)
- **AI conversations**: OpenAI API calls (costs money)
- **Audio processing**: Whisper and ElevenLabs (costs money)
- **Embedding generation**: OpenAI embeddings (disabled for load testing to avoid API costs and timeouts)

### AI Session Management
Session management operations:
- Starting cooking sessions
- Getting session information
- Updating cooking steps
- Cleaning up sessions

## 📊 Reports

After running the test, check:

1. **HTML Report**: `load_test_report.html`
   - Detailed performance metrics
   - Response time distributions
   - Error analysis

2. **CSV Data**: `load_test_results.csv`
   - Raw data for further analysis
   - Import into Excel/Google Sheets

## 🔄 Continuous Testing

For ongoing performance monitoring:

1. **Automated Runs**:
   ```bash
   # Run daily at 2 AM
   0 2 * * * cd /path/to/recipe-app && python run_load_test.py
   ```

2. **CI/CD Integration**:
   ```yaml
   # GitHub Actions example
   - name: Load Test
     run: |
       pip install locust
       python run_load_test.py
   ```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in your FastAPI backend
3. Verify all prerequisites are met
4. Test with a smaller user count first

## 🎯 Performance Targets

Aim for these performance targets:

| Metric | Target | Acceptable |
|--------|--------|------------|
| Average Response Time | < 300ms | < 500ms |
| 95th Percentile | < 800ms | < 1s |
| Success Rate | > 99.5% | > 99% |
| Concurrent Users | 100+ | 50+ |

Happy testing! 🍳
