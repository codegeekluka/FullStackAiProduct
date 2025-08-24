"""
Integration tests for Recipe API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.database.db_models import User, Recipe, Ingredient, Instruction


class TestRecipeAPI:
    """Test Recipe API endpoints"""
    
    def test_create_recipe_from_url(self, client: TestClient, db_session: Session):
        """Test creating a recipe from URL"""
        with pytest.MonkeyPatch.context() as m:
            # Mock the scraper to return test data
            m.setattr("backend.Apis.RecipeRequest.extract_webpage_data", lambda url: {
                "name": "Test Recipe",
                "description": "A delicious test recipe",
                "recipeInstructions": ["Step 1", "Step 2", "Step 3"],
                "recipeIngredient": ["Ingredient 1", "Ingredient 2"],
                "image": "https://example.com/image.jpg",
                "prep_time": "15 minutes",
                "cook_time": "30 minutes",
                "total_time": "45 minutes"
            })
            
            response = client.post(
                "/RecipePage",
                json={"url": "https://example.com/recipe"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "recipe_id" in data
            assert "slug" in data
            assert data["slug"] == "test-recipe"
    
    def test_create_recipe_from_url_invalid_url(self, client: TestClient):
        """Test creating a recipe from invalid URL"""
        with pytest.MonkeyPatch.context() as m:
            m.setattr("backend.Apis.RecipeRequest.extract_webpage_data", lambda url: "No HowToSteps found.")
            
            response = client.post(
                "/RecipePage",
                json={"url": "https://example.com/invalid"}
            )
            
            assert response.status_code == 400
            assert "No recipe found" in response.json()["detail"]
    
    def test_get_recipe_by_slug(self, client: TestClient, sample_recipe: Recipe):
        """Test getting a recipe by slug"""
        response = client.get(f"/recipes/{sample_recipe.slug}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_recipe.title
        assert data["slug"] == sample_recipe.slug
        assert "ingredients" in data
        assert "instructions" in data
        assert len(data["ingredients"]) == 3
        assert len(data["instructions"]) == 3
    
    def test_get_recipe_by_slug_not_found(self, client: TestClient):
        """Test getting a recipe that doesn't exist"""
        response = client.get("/recipes/non-existent-recipe")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"
    
    def test_get_user_recipes(self, client: TestClient, sample_recipe: Recipe):
        """Test getting user's recipes"""
        response = client.get("/user/recipes")
        
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["title"] == sample_recipe.title
    
    def test_update_recipe(self, client: TestClient, sample_recipe: Recipe):
        """Test updating a recipe"""
        update_data = {
            "title": "Updated Recipe Title",
            "description": "Updated description",
            "ingredients": ["Updated Ingredient 1", "Updated Ingredient 2"],
            "instructions": ["Updated Step 1", "Updated Step 2"]
        }
        
        response = client.put(
            f"/recipes/{sample_recipe.slug}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Recipe Title"
        assert data["description"] == "Updated description"
    
    def test_update_recipe_not_found(self, client: TestClient):
        """Test updating a recipe that doesn't exist"""
        update_data = {"title": "Updated Title"}
        
        response = client.put(
            "/recipes/non-existent-recipe",
            json=update_data
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"
    
    def test_delete_recipe(self, client: TestClient, sample_recipe: Recipe):
        """Test deleting a recipe"""
        response = client.delete(f"/recipes/{sample_recipe.slug}")
        
        assert response.status_code == 204
        
        # Verify recipe was deleted
        get_response = client.get(f"/recipes/{sample_recipe.slug}")
        assert get_response.status_code == 404
    
    def test_delete_recipe_not_found(self, client: TestClient):
        """Test deleting a recipe that doesn't exist"""
        response = client.delete("/recipes/non-existent-recipe")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"
    
    def test_create_manual_recipe(self, client: TestClient):
        """Test creating a recipe manually"""
        recipe_data = {
            "title": "Manual Recipe",
            "description": "A manually created recipe",
            "ingredients": ["Ingredient 1", "Ingredient 2"],
            "instructions": ["Step 1", "Step 2"],
            "prep_time": "10 minutes",
            "cook_time": "20 minutes",
            "total_time": "30 minutes",
            "image": "https://example.com/image.jpg",
            "tags": ["manual", "test"]
        }
        
        response = client.post(
            "/recipe/manualRecipe",
            json=recipe_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recipe_id" in data
        assert "slug" in data
        assert data["slug"] == "manual-recipe"
    
    def test_toggle_favorite(self, client: TestClient, sample_recipe: Recipe):
        """Test toggling recipe favorite status"""
        # Initially not favorite
        assert sample_recipe.favorite is False
        
        response = client.put(f"/recipe/{sample_recipe.slug}/favorite")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is True
        assert data["slug"] == sample_recipe.slug
    
    def test_toggle_active(self, client: TestClient, sample_recipe: Recipe):
        """Test toggling recipe active status"""
        # Initially active
        assert sample_recipe.is_active is True
        
        response = client.put(f"/recipe/{sample_recipe.slug}/active")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["slug"] == sample_recipe.slug
    
    def test_add_tags(self, client: TestClient, sample_recipe: Recipe):
        """Test adding tags to a recipe"""
        tags_data = {"tags": ["new-tag", "another-tag"]}
        
        response = client.put(
            f"/recipe/{sample_recipe.slug}/tags",
            json=tags_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "new-tag" in data["tags"]
        assert "another-tag" in data["tags"]
    
    def test_get_active_recipe(self, client: TestClient, sample_recipe: Recipe):
        """Test getting the active recipe"""
        response = client.get("/user/active-recipe")
        
        assert response.status_code == 200
        data = response.json()
        assert "active_recipe" in data
        assert data["active_recipe"]["title"] == sample_recipe.title
        assert data["active_recipe"]["slug"] == sample_recipe.slug


class TestUserTagsAPI:
    """Test User Tags API endpoints"""
    
    def test_get_user_tags(self, client: TestClient):
        """Test getting user tags"""
        response = client.get("/user/tags")
        
        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert len(data["tags"]) > 0
        
        # Check for default tags
        tag_names = [tag["tag_name"] for tag in data["tags"]]
        assert "cheap" in tag_names
        assert "fast" in tag_names
        assert "vegetarian" in tag_names
    
    def test_add_user_tag(self, client: TestClient):
        """Test adding a custom user tag"""
        tag_data = {"tag_name": "custom-tag"}
        
        response = client.post("/user/tags", json=tag_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["tag_name"] == "custom-tag"
        assert data["is_default"] is False
    
    def test_add_duplicate_tag(self, client: TestClient):
        """Test adding a duplicate tag"""
        tag_data = {"tag_name": "duplicate-tag"}
        
        # Add tag first time
        response1 = client.post("/user/tags", json=tag_data)
        assert response1.status_code == 200
        
        # Try to add same tag again
        response2 = client.post("/user/tags", json=tag_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
    
    def test_remove_user_tag(self, client: TestClient):
        """Test removing a custom user tag"""
        # First add a tag
        tag_data = {"tag_name": "tag-to-remove"}
        add_response = client.post("/user/tags", json=tag_data)
        assert add_response.status_code == 200
        
        # Then remove it
        response = client.delete("/user/tags/tag-to-remove")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Tag removed successfully"
    
    def test_remove_default_tag(self, client: TestClient):
        """Test removing a default tag (should fail)"""
        response = client.delete("/user/tags/cheap")
        
        assert response.status_code == 400
        assert "Cannot delete default tags" in response.json()["detail"]
    
    def test_remove_nonexistent_tag(self, client: TestClient):
        """Test removing a tag that doesn't exist"""
        response = client.delete("/user/tags/non-existent-tag")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Tag not found"
