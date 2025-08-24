#!/usr/bin/env python3
"""
Create performance indexes for the Recipe App database
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_performance_indexes():
    """Create indexes to improve query performance"""
    
    # Use the same database config as the app
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.database.config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME
    
    try:
        conn = psycopg2.connect(
            host=DATABASE_HOST,
            port=DATABASE_PORT,
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔧 Creating performance indexes...")
        
        # Indexes for Recipe queries
        indexes = [
            # Recipe slug lookups (most common)
            "CREATE INDEX IF NOT EXISTS idx_recipe_slug ON recipe(slug)",
            
            # User recipe queries
            "CREATE INDEX IF NOT EXISTS idx_recipe_user_id ON recipe(user_id)",
            
            # Recipe title searches
            "CREATE INDEX IF NOT EXISTS idx_recipe_title ON recipe(title)",
            
            # Recipe favorites and active status
            "CREATE INDEX IF NOT EXISTS idx_recipe_favorite ON recipe(favorite) WHERE favorite = true",
            "CREATE INDEX IF NOT EXISTS idx_recipe_active ON recipe(is_active) WHERE is_active = true",
            
            # Composite index for user + favorite recipes
            "CREATE INDEX IF NOT EXISTS idx_recipe_user_favorite ON recipe(user_id, favorite)",
            
            # Ingredient queries
            "CREATE INDEX IF NOT EXISTS idx_ingredient_recipe_id ON ingredient(recipe_id)",
            
            # Instruction queries
            "CREATE INDEX IF NOT EXISTS idx_instruction_recipe_id ON instruction(recipe_id)",
            "CREATE INDEX IF NOT EXISTS idx_instruction_step_number ON instruction(recipe_id, step_number)",
            
            # User preference indexes
            "CREATE INDEX IF NOT EXISTS idx_user_dietary_restriction_user_id ON user_dietary_restriction(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_cuisine_preference_user_id ON user_cuisine_preference(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_health_goal_user_id ON user_health_goal(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_budget_preference_user_id ON user_budget_preference(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_skill_level_user_id ON user_skill_level(user_id)",
            
            # User tag indexes
            "CREATE INDEX IF NOT EXISTS idx_user_tag_user_id ON user_tag(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_tag_name ON user_tag(tag_name)",
            
            # Session indexes
            "CREATE INDEX IF NOT EXISTS idx_user_session_user_id ON user_session(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_session_recipe_id ON user_session(recipe_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_session_session_id ON user_session(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_session_active ON user_session(is_active) WHERE is_active = true",
            
            # Recipe tag association indexes
            "CREATE INDEX IF NOT EXISTS idx_recipe_tags_recipe_id ON recipe_tags(recipe_id)",
            "CREATE INDEX IF NOT EXISTS idx_recipe_tags_tag_id ON recipe_tags(tag_id)",
            
            # Tag name lookups
            "CREATE INDEX IF NOT EXISTS idx_tag_name ON tag(name)",
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
            except Exception as e:
                print(f"⚠️ Index creation failed: {e}")
        
        # Analyze tables to update statistics
        print("\n📊 Analyzing tables for query optimization...")
        tables = [
            "recipe", "ingredient", "instruction", "user", "user_tag",
            "user_dietary_restriction", "user_cuisine_preference", 
            "user_health_goal", "user_budget_preference", "user_skill_level",
            "user_session", "tag", "recipe_tags"
        ]
        
        for table in tables:
            try:
                cursor.execute(f"ANALYZE {table}")
                print(f"✅ Analyzed table: {table}")
            except Exception as e:
                print(f"⚠️ Table analysis failed for {table}: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Performance indexes created successfully!")
        print("💡 These indexes will improve query performance for:")
        print("   - Recipe lookups by slug")
        print("   - User recipe queries")
        print("   - Recipe favorites and active status")
        print("   - User preferences and tags")
        print("   - Session management")
        
    except Exception as e:
        print(f"❌ Failed to create indexes: {e}")

if __name__ == "__main__":
    create_performance_indexes()

