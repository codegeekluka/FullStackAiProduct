# locustfile.py
import json
import random
import time
from typing import List, Dict, Any
from locust import HttpUser, task, between, events
from locust.exception import StopUser

class RecipeAppUser(HttpUser):
    """Simulates a realistic user of the Recipe App"""
    
    # Simulate realistic user think-time between tasks
    wait_time = between(2, 8)
    
    # Test user credentials - these will be created during test setup
    test_users = [
        {"username": "testuser1", "password": "testpass123"},
        {"username": "testuser2", "password": "testpass123"},
        {"username": "testuser3", "password": "testpass123"},
        {"username": "testuser4", "password": "testpass123"},
        {"username": "testuser5", "password": "testpass123"},
    ]
    
    # Sample recipe URLs for testing recipe import (REMOVED - web scraping causes issues)
    # sample_recipe_urls = [
    #     "https://www.indianhealthyrecipes.com/chicken-tikka-masala/",
    #     "https://www.allrecipes.com/recipe/24074/alysias-basic-meat-lasagna/",
    #     "https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes-recipe-1913844",
    #     "https://www.bbcgoodfood.com/recipes/classic-chocolate-chip-cookies",
    #     "https://www.simplyrecipes.com/recipes/homemade_pizza/"
    # ]
    
    # Sample recipe data for manual creation (matches RecipeUpdate model)
    sample_recipes = [
        {
            "title": "Classic Spaghetti Carbonara",
            "description": "A traditional Italian pasta dish with eggs, cheese, and pancetta",
            "ingredients": ["400g spaghetti", "200g pancetta", "4 large eggs", "100g pecorino cheese", "Black pepper", "Salt"],
            "instructions": [
                "Bring a large pot of salted water to boil",
                "Cook spaghetti according to package directions",
                "Meanwhile, cook pancetta in a large skillet until crispy",
                "Beat eggs and cheese in a bowl",
                "Drain pasta, reserving 1 cup of pasta water",
                "Add hot pasta to skillet with pancetta",
                "Remove from heat and quickly stir in egg mixture",
                "Add pasta water as needed for creamy consistency",
                "Season with black pepper and serve immediately"
            ],
            "prep_time": "10 minutes",
            "cook_time": "15 minutes",
            "total_time": "25 minutes",
            "tags": ["italian", "pasta", "quick-meal"],
            "is_active": False,
            "favorite": False
        },
        {
            "title": "Chicken Stir Fry",
            "description": "Quick and healthy chicken stir fry with vegetables",
            "ingredients": ["500g chicken breast", "2 bell peppers", "1 broccoli head", "3 tbsp soy sauce", "2 tbsp oil", "2 cloves garlic", "1 inch ginger"],
            "instructions": [
                "Cut chicken into bite-sized pieces",
                "Chop vegetables into similar-sized pieces",
                "Heat oil in a wok or large skillet",
                "Stir fry chicken until golden brown",
                "Add garlic and ginger, cook for 30 seconds",
                "Add vegetables and stir fry for 3-4 minutes",
                "Add soy sauce and cook for 1 more minute",
                "Serve hot with rice"
            ],
            "prep_time": "15 minutes",
            "cook_time": "10 minutes",
            "total_time": "25 minutes",
            "tags": ["asian", "healthy", "quick-meal"],
            "is_active": False,
            "favorite": False
        },
        {
            "title": "Chocolate Chip Cookies",
            "description": "Soft and chewy chocolate chip cookies",
            "ingredients": ["2 1/4 cups flour", "1 cup butter", "3/4 cup sugar", "3/4 cup brown sugar", "2 eggs", "1 tsp vanilla", "1 tsp baking soda", "1/2 tsp salt", "2 cups chocolate chips"],
            "instructions": [
                "Preheat oven to 375°F (190°C)",
                "Cream butter and sugars until light and fluffy",
                "Beat in eggs and vanilla",
                "Mix in flour, baking soda, and salt",
                "Stir in chocolate chips",
                "Drop rounded tablespoons onto ungreased baking sheets",
                "Bake for 9-11 minutes until golden brown",
                "Cool on baking sheets for 2 minutes, then transfer to wire racks"
            ],
            "prep_time": "20 minutes",
            "cook_time": "10 minutes",
            "total_time": "30 minutes",
            "tags": ["dessert", "baking", "chocolate"],
            "is_active": False,
            "favorite": False
        }
    ]
    
    # AI Assistant session management (NO PAID SERVICES - safe for testing)
    # These endpoints do NOT use OpenAI, ElevenLabs, Whisper, or any paid APIs
    ai_session_actions = [
        "start_session",      # Creates session - no API calls
        "get_sessions",       # Database query only
        "update_step",        # Database update only
        "cleanup_session"     # Database cleanup only
    ]
    
    def on_start(self):
        """Initialize user session - register and login"""
        self.user_data = random.choice(self.test_users)
        self.access_token = None
        self.user_recipes = []
        self.current_session_id = None
        
        # Register user (might fail if already exists, that's ok)
        try:
            response = self.client.post("/register", json={
                "username": self.user_data["username"],
                "password": self.user_data["password"]
            })
            if response.status_code == 200:
                print(f"Created new test user: {self.user_data['username']}")
            elif response.status_code == 400:
                error_detail = response.json() if response.content else "No error details"
                print(f"Test user {self.user_data['username']} already exists (400): {error_detail}")
            else:
                print(f"Unexpected response during registration: {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Registration error (this might be expected): {e}")
        
        # Login and get access token
        try:
            response = self.client.post("/login", data={
                "username": self.user_data["username"],
                "password": self.user_data["password"]
            })
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                if self.access_token:
                    self.client.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    print(f"User {self.user_data['username']} logged in successfully")
                else:
                    print(f"Failed to get access token for {self.user_data['username']}")
                    raise StopUser()
            else:
                error_detail = response.json() if response.content else "No error details"
                print(f"Login failed for {self.user_data['username']}: {response.status_code}")
                print(f"Error details: {error_detail}")
                raise StopUser()
        except Exception as e:
            print(f"Error during login: {e}")
            raise StopUser()
    
    @task(4)  # Increased weight for stable operations
    def browse_recipes(self):
        """Browse user's recipes - most common action"""
        response = self.client.get("/user/recipes")
        if response.status_code == 200:
            recipes = response.json()
            self.user_recipes = recipes
            if recipes:
                # View a random recipe
                recipe = random.choice(recipes)
                self.client.get(f"/recipes/{recipe['slug']}")
    
    @task(3)  # Increased weight for stable operations
    def view_recipe_details(self):
        """View specific recipe details"""
        if self.user_recipes:
            recipe = random.choice(self.user_recipes)
            self.client.get(f"/recipes/{recipe['slug']}")
    
    @task(2)  # Increased weight since embeddings are disabled
    def create_manual_recipe(self):
        """Create a new recipe manually"""
        recipe_data = random.choice(self.sample_recipes).copy()  # Create a copy to avoid modifying original
        
        # Add unique identifier to avoid slug conflicts (still needed for concurrent users)
        recipe_data["title"] = f"{recipe_data['title']} {random.randint(1000, 9999)}"
        
        response = self.client.post("/recipe/manualRecipe", json=recipe_data)
        if response.status_code == 200:
            # Add to our local list
            new_recipe = response.json()
            self.user_recipes.append(new_recipe)
        elif response.status_code == 400:
            error_detail = response.json() if response.content else "No error details"
            print(f"Recipe creation failed (400): {error_detail}")
        elif response.status_code == 500:
            print(f"Recipe creation failed (500): Server error - check backend logs")
        else:
            print(f"Recipe creation failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    # @task(1)  # REMOVED - web scraping causes 400 errors and is unreliable
    # def import_recipe_from_url(self):
    #     """Import recipe from a URL"""
    #     # REMOVED: Web scraping functionality causes issues with external sites
    #     # This endpoint is excluded from load testing to avoid 400 errors
    #     pass
    
    @task(2)
    def manage_recipe_favorites(self):
        """Toggle recipe favorite status"""
        if self.user_recipes:
            recipe = random.choice(self.user_recipes)
            self.client.put(f"/recipe/{recipe['slug']}/favorite")
    
    @task(1)
    def set_active_recipe(self):
        """Set a recipe as active for cooking"""
        if self.user_recipes:
            recipe = random.choice(self.user_recipes)
            self.client.put(f"/recipe/{recipe['slug']}/active")
    
    @task(1)
    def manage_recipe_tags(self):
        """Add or update recipe tags"""
        if self.user_recipes:
            recipe = random.choice(self.user_recipes)
            tags = random.sample(["quick-meal", "healthy", "vegetarian", "dessert", "italian", "asian"], 2)
            self.client.put(f"/recipe/{recipe['slug']}/tags", json={"tags": tags})
    
    @task(2)
    def use_ai_assistant(self):
        """Interact with the AI cooking assistant (session management only - NO PAID SERVICES)"""
        # SAFE ENDPOINTS ONLY - No OpenAI, ElevenLabs, Whisper, or other paid APIs
        if self.user_recipes:
            recipe = random.choice(self.user_recipes)
            
            # Start a cooking session
            session_response = self.client.post("/ai/start_session", json={
                "recipe_id": recipe["id"]
            })
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                self.current_session_id = session_data["session_id"]
                
                # Get session info (doesn't use OpenAI credits)
                self.client.get("/ai/sessions")
                
                # Update session step (doesn't use OpenAI credits)
                if random.random() < 0.5:  # 50% chance
                    step_number = random.randint(1, 5)
                    self.client.put(f"/ai/sessions/{self.current_session_id}/step", json={
                        "step_number": step_number
                    })
    
    @task(1)
    def manage_user_profile(self):
        """Update user profile and preferences"""
        # Get current profile
        self.client.get("/users/me")
        
        # Update profile occasionally
        if random.random() < 0.2:  # 20% chance
            profile_update = {
                "firstname": f"Test{random.randint(1, 100)}",
                "lastname": f"User{random.randint(1, 100)}",
                "age": random.randint(18, 65)
            }
            self.client.put("/users/me/profile", json=profile_update)
    
    @task(1)
    def manage_user_tags(self):
        """Manage user's custom tags"""
        # Get user tags
        response = self.client.get("/user/tags")
        if response.status_code == 200:
            tags = response.json()
            
            # Create a new tag occasionally
            if random.random() < 0.3:  # 30% chance
                new_tag = f"custom-tag-{random.randint(1, 1000)}"
                self.client.post("/user/tags", json={"tag_name": new_tag})
    
    @task(1)
    def get_active_recipe(self):
        """Get the currently active recipe"""
        self.client.get("/user/active-recipe")
    
    @task(1)
    def get_preference_options(self):
        """Get available preference options for onboarding"""
        self.client.get("/users/me/preferences/options")
    
    @task(1)
    def verify_token(self):
        """Verify the current access token"""
        self.client.post("/verify-token")
    
    @task(1)
    def health_check(self):
        """Check API health"""
        self.client.get("/health")
    
    def on_stop(self):
        """Cleanup when user stops"""
        if self.current_session_id:
            try:
                self.client.delete(f"/ai/sessions/{self.current_session_id}")
            except:
                pass


# Additional user class for heavy AI session management testing
class AIHeavyUser(RecipeAppUser):
    """User that primarily uses AI session management features (NO PAID SERVICES)"""
    
    wait_time = between(1, 3)  # Faster interactions for AI testing
    
    @task(5)
    def intensive_ai_session_management(self):
        """Heavy AI session management usage (NO PAID SERVICES - safe for testing)"""
        # SAFE ENDPOINTS ONLY - No OpenAI, ElevenLabs, Whisper, or other paid APIs
        if self.user_recipes:
            recipe = random.choice(self.user_recipes)
            
            # Start session
            session_response = self.client.post("/ai/start_session", json={
                "recipe_id": recipe["id"]
            })
            
            if session_response.status_code == 200:
                session_data = session_response.json()
                session_id = session_data["session_id"]
                
                # Get session info multiple times
                for _ in range(random.randint(2, 5)):
                    self.client.get("/ai/sessions")
                    time.sleep(0.5)  # Small delay between requests
                
                # Update session step multiple times
                for step in range(1, 6):
                    self.client.put(f"/ai/sessions/{session_id}/step", json={
                        "step_number": step
                    })
                    time.sleep(0.3)  # Small delay between steps
                
                # Clean up session
                self.client.delete(f"/ai/sessions/{session_id}")


# Additional user class for recipe management testing
class RecipeManagerUser(RecipeAppUser):
    """User that primarily manages recipes"""
    
    wait_time = between(3, 6)
    
    @task(4)  # Increased weight since embeddings are disabled
    def intensive_recipe_management(self):
        """Heavy recipe management operations"""
        # Create multiple recipes
        for _ in range(random.randint(1, 3)):  # Increased back to 1-3 since embeddings are disabled
            recipe_data = random.choice(self.sample_recipes).copy()  # Create a copy to avoid modifying original
            # Add unique identifier to avoid slug conflicts
            recipe_data["title"] = f"{recipe_data['title']} {random.randint(1000, 9999)}"
            
            response = self.client.post("/recipe/manualRecipe", json=recipe_data)
            if response.status_code == 200:
                new_recipe = response.json()
                self.user_recipes.append(new_recipe)
            elif response.status_code == 500:
                print(f"Recipe creation failed (500): Server error - check backend logs")
        
        # Update existing recipes
        if self.user_recipes:
            for recipe in random.sample(self.user_recipes, min(2, len(self.user_recipes))):
                # Toggle favorite
                self.client.put(f"/recipe/{recipe['slug']}/favorite")
                # Update tags
                tags = random.sample(["quick-meal", "healthy", "vegetarian", "dessert"], 2)
                self.client.put(f"/recipe/{recipe['slug']}/tags", json={"tags": tags})


# Event listeners for test setup and teardown
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Setup test data before starting"""
    print("Setting up test data...")
    
    # Create test users if they don't exist
    client = environment.client
    for user_data in RecipeAppUser.test_users:
        try:
            client.post("/register", json=user_data)
            print(f"Created test user: {user_data['username']}")
        except:
            print(f"Test user {user_data['username']} already exists or creation failed")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Cleanup after test"""
    print("Test completed. Cleaning up...")
