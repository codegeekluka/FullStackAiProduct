import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/recipes/AddRecipePage.css';
import PillNav from '../components/layout/PillNav.jsx';
import BottomNav from '../components/layout/BottomNav.jsx';
import ScrapeWebsiteBtn from '../components/utils/ScrapeWebsiteBtn.jsx';
import { AuthContext } from '../contexts/AuthContext.jsx';

const AddRecipePage = () => {
  const navigate = useNavigate();
  const { userProfile, setNavOrigin } = useContext(AuthContext);

  // Helper function to construct full image URL
  const getImageUrl = (relativeUrl) => {
    if (!relativeUrl) return null;
    // If it's already a full URL, return as is
    if (relativeUrl.startsWith('http')) return relativeUrl;
    // Otherwise, prepend the backend URL
    return `http://localhost:8000${relativeUrl}`;
  };

  // Get hero image with fallbacks
  const getHeroImageStyle = () => {
    if (userProfile?.hero_image_url) {
      const fullImageUrl = getImageUrl(userProfile.hero_image_url);
      return {
        backgroundImage: `url('${fullImageUrl}')`,
        backgroundSize: '1200px 400px',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      };
    } else {
      // Fallback to default image
      return {
        backgroundImage: `url('pexels-enginakyurt-1435895.jpg')`,
        backgroundSize: '1200px 400px',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      };
    }
  };

  return (
    <div className="add-recipe-page">
      <div className="add-recipe-hero" style={getHeroImageStyle()}>
        <h1>Add New Recipe</h1>
        <p>Create your own delicious recipe</p>
      </div>
      <PillNav />
      <BottomNav />
      <div className="add-recipe-content">
        <div className="recipe-creation-buttons">
          <ScrapeWebsiteBtn />
          <button 
            onClick={() => {
              console.log('Add Recipe Page - Add own recipe button clicked');
              setNavOrigin('/add-recipe');
              console.log('Add Recipe Page - origin set to /add-recipe for new recipe');
              navigate('/recipe/new', { recipe: true });
            }} 
            className="add-own-recipe-btn"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Add Own Recipe
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddRecipePage;
