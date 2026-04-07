import '../../styles/recipes/RecipeCard.css';
import { AuthContext } from '../../contexts/AuthContext';
import { useContext } from 'react';
import { FavoriteIcon } from '../ui/Icons';
import { toggleFavorite } from '../../services/toggleFavorite';

const RecipeCard = ({recipe, onClick }) => {
  const { recipes, fetchUserRecipes } = useContext(AuthContext)
  const token = localStorage.getItem("token");

  const handleFavoriteClick = async (e) => {
    e.stopPropagation(); // Prevent card click when clicking favorite button
    try {
      await toggleFavorite(recipe.slug, token);
      // Refresh the recipes list to update the UI
      if (fetchUserRecipes) {
        fetchUserRecipes(token);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  return (
    <div className="recipe-card" onClick={onClick}>
      <div className="recipe-image-container">
        <img className="recipe-image" src={recipe.image || '/default-recipe-image.svg'} alt={recipe.title} />
        {recipe.favorite && (
          <button 
            className="favorite-button" 
            onClick={handleFavoriteClick}
            title="Unfavorite"
          >
            <FavoriteIcon active={true} />
          </button>
        )}
      </div>
      <div className="recipe-content">
        <h3 className="recipe-title">{recipe.title}</h3>
        <p className="recipe-description">
          {`Total Time: ${recipe.total_time  || "N/A"}`}
        </p>
        <button className="see-recipe-button">
          See Recipe
        </button>
      </div>
    </div>
  );
}

export default RecipeCard;