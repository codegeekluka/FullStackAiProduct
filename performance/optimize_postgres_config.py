#!/usr/bin/env python3
"""
PostgreSQL optimization script for high-concurrency Recipe App
This script optimizes PostgreSQL settings for better performance under load.
"""

import psycopg2
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.database.config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME

def optimize_postgres_settings():
    """Apply PostgreSQL optimizations for high concurrency"""
    
    print("🔧 Optimizing PostgreSQL for high concurrency...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Check current settings
        print("\n📊 Current PostgreSQL Settings:")
        settings_to_check = [
            'max_connections',
            'shared_buffers',
            'effective_cache_size',
            'work_mem',
            'maintenance_work_mem',
            'checkpoint_completion_target',
            'wal_buffers',
            'default_statistics_target'
        ]
        
        for setting in settings_to_check:
            cursor.execute(f"SHOW {setting};")
            value = cursor.fetchone()[0]
            print(f"  {setting}: {value}")
        
        print("\n💡 Recommended optimizations:")
        print("  Add these to your postgresql.conf file:")
        print("  # Connection and Memory")
        print("  max_connections = 200")
        print("  shared_buffers = 256MB")
        print("  effective_cache_size = 1GB")
        print("  work_mem = 4MB")
        print("  maintenance_work_mem = 64MB")
        print("  ")
        print("  # WAL and Checkpoints")
        print("  checkpoint_completion_target = 0.9")
        print("  wal_buffers = 16MB")
        print("  ")
        print("  # Query Planning")
        print("  default_statistics_target = 100")
        print("  random_page_cost = 1.1")
        print("  ")
        print("  # Logging (for debugging)")
        print("  log_min_duration_statement = 1000  # Log slow queries")
        print("  log_lock_waits = on")
        print("  log_temp_files = 0")
        
        # Try to apply some optimizations that can be set at session level
        session_optimizations = [
            "SET work_mem = '8MB';",
            "SET random_page_cost = 1.1;",
            "SET effective_cache_size = '1GB';"
        ]
        
        print(f"\n🚀 Applying session-level optimizations...")
        for optimization in session_optimizations:
            try:
                cursor.execute(optimization)
                print(f"  ✅ Applied: {optimization}")
            except Exception as e:
                print(f"  ❌ Failed: {optimization} - {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ PostgreSQL optimization check complete!")
        print("Note: For persistent changes, modify postgresql.conf and restart PostgreSQL")
        
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running and accessible")

def check_database_indexes():
    """Check if performance indexes exist"""
    
    print("\n🔍 Checking database indexes...")
    
    try:
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Check for important indexes
        index_queries = [
            ("recipe_user_id_idx", "SELECT indexname FROM pg_indexes WHERE indexname = 'recipe_user_id_idx';"),
            ("recipe_slug_idx", "SELECT indexname FROM pg_indexes WHERE indexname = 'recipe_slug_idx';"),
            ("recipe_is_active_idx", "SELECT indexname FROM pg_indexes WHERE indexname = 'recipe_is_active_idx';"),
            ("ingredient_recipe_id_idx", "SELECT indexname FROM pg_indexes WHERE indexname = 'ingredient_recipe_id_idx';"),
            ("instruction_recipe_id_idx", "SELECT indexname FROM pg_indexes WHERE indexname = 'instruction_recipe_id_idx';"),
        ]
        
        missing_indexes = []
        for index_name, query in index_queries:
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                print(f"  ✅ {index_name}: EXISTS")
            else:
                print(f"  ❌ {index_name}: MISSING")
                missing_indexes.append(index_name)
        
        if missing_indexes:
            print(f"\n⚠️ Missing {len(missing_indexes)} important indexes!")
            print("Run 'python create_performance_indexes.py' to create them")
        else:
            print("\n✅ All important indexes are present!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking indexes: {e}")

if __name__ == "__main__":
    optimize_postgres_settings()
    check_database_indexes()
