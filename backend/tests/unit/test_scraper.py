"""
Unit tests for web scraper functionality
"""
import pytest
from unittest.mock import patch, Mock
from backend.Scrapers.scraper import extract_webpage_data


class TestWebScraper:
    """Test web scraper functionality"""
    
    def test_extract_webpage_data_success(self):
        """Test successful recipe extraction"""
        mock_html = """
        <html>
            <head>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org/",
                    "@type": "Recipe",
                    "name": "Test Recipe",
                    "description": "A delicious test recipe",
                    "recipeInstructions": [
                        {"@type": "HowToStep", "text": "Step 1"},
                        {"@type": "HowToStep", "text": "Step 2"}
                    ],
                    "recipeIngredient": ["Ingredient 1", "Ingredient 2"],
                    "image": "https://example.com/image.jpg"
                }
                </script>
            </head>
            <body>
                <h1>Test Recipe</h1>
            </body>
        </html>
        """
        
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = mock_html
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = extract_webpage_data("https://example.com/recipe")
            
            assert isinstance(result, dict)
            assert result["name"] == "Test Recipe"
            assert result["description"] == "A delicious test recipe"
            assert len(result["recipeInstructions"]) == 2
            assert len(result["recipeIngredient"]) == 2
            assert result["image"] == "https://example.com/image.jpg"
    
    def test_extract_webpage_data_no_recipe(self):
        """Test extraction when no recipe is found"""
        mock_html = """
        <html>
            <head>
                <title>Regular Webpage</title>
            </head>
            <body>
                <h1>No Recipe Here</h1>
            </body>
        </html>
        """
        
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = mock_html
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = extract_webpage_data("https://example.com/no-recipe")
            
            assert result == "No HowToSteps found."
    
    def test_extract_webpage_data_connection_error(self):
        """Test handling of connection errors"""
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection error")
            
            result = extract_webpage_data("https://example.com/recipe")
            
            assert "connection error" in result.lower()
    
    def test_extract_webpage_data_timeout(self):
        """Test handling of timeout errors"""
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_get.side_effect = Exception("timeout")
            
            result = extract_webpage_data("https://example.com/recipe")
            
            assert "timed out" in result.lower()
    
    def test_extract_webpage_data_invalid_url(self):
        """Test handling of invalid URLs"""
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_get.side_effect = Exception("Invalid URL")
            
            result = extract_webpage_data("invalid-url")
            
            assert "failed" in result.lower()
    
    def test_extract_webpage_data_malformed_json(self):
        """Test handling of malformed JSON in recipe data"""
        mock_html = """
        <html>
            <head>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org/",
                    "@type": "Recipe",
                    "name": "Test Recipe",
                    "recipeInstructions": [
                        {"@type": "HowToStep", "text": "Step 1"}
                    ],
                    "recipeIngredient": ["Ingredient 1"]
                }
                </script>
            </head>
        </html>
        """
        
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = mock_html
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = extract_webpage_data("https://example.com/recipe")
            
            # Should still work even with missing optional fields
            assert isinstance(result, dict)
            assert result["name"] == "Test Recipe"
            assert len(result["recipeInstructions"]) == 1
            assert len(result["recipeIngredient"]) == 1
    
    def test_extract_webpage_data_multiple_recipes(self):
        """Test extraction when multiple recipes are found"""
        mock_html = """
        <html>
            <head>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org/",
                    "@type": "Recipe",
                    "name": "First Recipe",
                    "recipeInstructions": [{"@type": "HowToStep", "text": "Step 1"}],
                    "recipeIngredient": ["Ingredient 1"]
                }
                </script>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org/",
                    "@type": "Recipe",
                    "name": "Second Recipe",
                    "recipeInstructions": [{"@type": "HowToStep", "text": "Step 1"}],
                    "recipeIngredient": ["Ingredient 1"]
                }
                </script>
            </head>
        </html>
        """
        
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = mock_html
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = extract_webpage_data("https://example.com/recipe")
            
            # Should return the first recipe found
            assert isinstance(result, dict)
            assert result["name"] == "First Recipe"
    
    def test_extract_webpage_data_http_error(self):
        """Test handling of HTTP errors"""
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            result = extract_webpage_data("https://example.com/not-found")
            
            assert "failed" in result.lower()
    
    def test_extract_webpage_data_empty_response(self):
        """Test handling of empty response"""
        with patch('backend.Scrapers.scraper.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = ""
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = extract_webpage_data("https://example.com/empty")
            
            assert result == "No HowToSteps found."
