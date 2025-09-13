#!/usr/bin/env python3
"""
Setup script for PostgreSQL test database
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_test_database():
    """Create the test database if it doesn't exist"""
    # Database configuration
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_USER = "postgres"
    DB_PASSWORD = "password"
    TEST_DB_NAME = "recipe_app_test"
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if test database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating test database '{TEST_DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
            print(f"Test database '{TEST_DB_NAME}' created successfully!")
        else:
            print(f"Test database '{TEST_DB_NAME}' already exists.")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("\nPlease make sure:")
        print("1. PostgreSQL is installed and running")
        print("2. You have a user 'postgres' with password 'password'")
        print("3. PostgreSQL is running on localhost:5432")
        print("\nOr update the database configuration in setup_test_db.py")
        sys.exit(1)

def drop_test_database():
    """Drop the test database"""
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_USER = "postgres"
    DB_PASSWORD = "password"
    TEST_DB_NAME = "recipe_app_test"
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Drop test database
        cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
        print(f"Test database '{TEST_DB_NAME}' dropped successfully!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Error dropping test database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_test_database()
    else:
        create_test_database()
