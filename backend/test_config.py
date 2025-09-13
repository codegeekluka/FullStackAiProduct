"""
Test configuration for PostgreSQL database
"""
import os

# PostgreSQL Test Database Configuration
# Update these values to match your PostgreSQL setup

DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
DB_PORT = os.getenv("TEST_DB_PORT", "5432")
DB_USER = os.getenv("TEST_DB_USER", "postgres")
DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "password")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "recipe_app_test")

# SQLAlchemy URL for testing
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

# Instructions for setup:
# 1. Make sure PostgreSQL is installed and running
# 2. Create a test database user (optional, can use existing postgres user)
# 3. Update the values above or set environment variables:
#    - TEST_DB_HOST: PostgreSQL host (default: localhost)
#    - TEST_DB_PORT: PostgreSQL port (default: 5432)
#    - TEST_DB_USER: Database user (default: postgres)
#    - TEST_DB_PASSWORD: Database password (default: password)
#    - TEST_DB_NAME: Test database name (default: recipe_app_test)
