# Recipe App Backend Test Suite

This directory contains comprehensive unit and integration tests for the Recipe App backend.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and shared fixtures
├── unit/                       # Unit tests
│   ├── test_db_models.py      # Database model tests
│   └── test_ai_assistant.py   # AI assistant service tests
├── integration/               # Integration tests
│   ├── test_recipe_api.py     # Recipe API endpoint tests
│   ├── test_ai_assistant_api.py # AI assistant API tests
│   └── test_user_profile_api.py # User profile API tests
└── README.md                  # This file
```

## Running Tests

### Prerequisites

1. **PostgreSQL Setup**:
   - Make sure PostgreSQL is installed and running
   - Create the test database:
   ```bash
   python setup_test_db.py
   ```

2. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

3. Make sure you're in the backend directory:
```bash
cd backend
```

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=backend --cov-report=term-missing
```

### Running Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Tests with specific markers
pytest -m unit
pytest -m integration
pytest -m api
```

### Running Individual Test Files

```bash
# Run specific test file
pytest tests/unit/test_db_models.py

# Run specific test class
pytest tests/unit/test_db_models.py::TestUserModel

# Run specific test method
pytest tests/unit/test_db_models.py::TestUserModel::test_create_user
```

### Using the Test Runner Script

```bash
# Run the automated test suite
python run_tests.py
```

## Test Coverage

The test suite includes:

### Unit Tests
- **Database Models**: Testing all model classes and their relationships
- **AI Assistant Service**: Testing core AI functionality, embeddings, and response generation

### Integration Tests
- **Recipe API**: Testing all recipe-related endpoints (CRUD operations, scraping, etc.)
- **AI Assistant API**: Testing AI assistant endpoints (sessions, chat, audio processing)
- **User Profile API**: Testing user profile management and preferences

## Test Features

### Fixtures
- `db_session`: Fresh database session for each test
- `client`: FastAPI test client with mocked dependencies
- `sample_user`: Test user instance
- `sample_recipe`: Test recipe with ingredients and instructions
- `mock_openai`: Mocked OpenAI API calls
- `mock_elevenlabs`: Mocked ElevenLabs API calls

### Mocking
- External API calls (OpenAI, ElevenLabs)
- File uploads and S3 operations
- Database operations (where appropriate)

### Test Database
- Uses SQLite in-memory database for fast, isolated tests
- Each test gets a fresh database session
- Automatic cleanup after each test

## Test Markers

Use these markers to run specific test categories:

```bash
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m api           # API tests
pytest -m database      # Database tests
pytest -m ai            # AI service tests
pytest -m slow          # Slow running tests
```

## Coverage Reports

Generate coverage reports:

```bash
# Terminal coverage report
pytest --cov=backend --cov-report=term-missing

# HTML coverage report
pytest --cov=backend --cov-report=html:htmlcov

# XML coverage report (for CI/CD)
pytest --cov=backend --cov-report=xml
```

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    cd backend
    pip install -r requirements-test.txt
    pytest --cov=backend --cov-report=xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the backend directory and have installed all dependencies
2. **Database Errors**: Tests use SQLite in-memory database, no external database setup required
3. **Mock Errors**: Some tests mock external services, ensure mocks are properly configured

### Debug Mode

Run tests in debug mode for more information:

```bash
pytest -v -s --tb=long
```

### Running Tests in Parallel

For faster execution (if you have multiple CPU cores):

```bash
pip install pytest-xdist
pytest -n auto
```

## Adding New Tests

### Unit Tests
1. Create test file in `tests/unit/`
2. Follow naming convention: `test_<module_name>.py`
3. Use appropriate fixtures from `conftest.py`
4. Mock external dependencies

### Integration Tests
1. Create test file in `tests/integration/`
2. Test API endpoints using the `client` fixture
3. Test full request/response cycles
4. Include both success and error cases

### Test Guidelines
- Use descriptive test names
- Test both success and failure scenarios
- Mock external dependencies
- Keep tests isolated and independent
- Use appropriate assertions
- Add docstrings to test methods

## Performance

- Unit tests: ~1-2 seconds
- Integration tests: ~5-10 seconds
- Full test suite: ~10-15 seconds

Tests are optimized for speed while maintaining comprehensive coverage.
