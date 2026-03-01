import React, { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";
import CookBookCard from "../components/pages/CookBookCard";
import "../styles/recipes/MyRecipes.css";
import MultiTagDropdown from "../components/ui/MultiTagDropdown";
import TagPills from "../components/ui/TagPills";
import TimeDropdown from "../components/ui/TimeDropdown";
import PillNav from "../components/layout/PillNav.jsx";
import BottomNav from "../components/layout/BottomNav.jsx";
import { API_BASE_URL } from "../config/api";

export default function MyRecipes() {
  const { recipes, setNavOrigin, fetchUserRecipes, user, userProfile } = useContext(AuthContext);
  const [searchQuery, setSearchQuery] = useState("");
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]);
  const [selectedTime, setSelectedTime] = useState("");
  const [visibleCount, setVisibleCount] = useState(20); // initial load count
  const [isMobile, setIsMobile] = useState(false);

  const navigate = useNavigate();

  // Helper function to construct full image URL
  const getImageUrl = (relativeUrl) => {
    if (!relativeUrl) return null;
    // If it's already a full URL, return as is
    if (relativeUrl.startsWith('http')) return relativeUrl;
    // Otherwise, prepend the backend URL
    return `${API_BASE_URL}${relativeUrl}`;
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

  // Fetch fresh recipes when component mounts
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (user && token) {
      fetchUserRecipes(token);
    }
  }, [user, fetchUserRecipes]);

  // Detect mobile vs desktop
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth <= 900);
    };
    
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Reset visible count when filters change
  useEffect(() => {
    const initialCount = isMobile ? 10 : 20;
    setVisibleCount(initialCount);
  }, [searchQuery, showFavoritesOnly, selectedTags, selectedTime, isMobile]);
// Extract all tags (handle object or string)
    const allTags = Array.from(
        new Set(
        recipes.flatMap((r) => (r.tags || []).map(t => typeof t === 'string' ? t : t.name))
        )
    );

// Helper function to parse time string and get total minutes
const parseTimeToMinutes = (timeString) => {
  if (!timeString) return 0;
  
  const hoursMatch = timeString.match(/(\d+)h/);
  const minutesMatch = timeString.match(/(\d+)m/);
  
  const hours = hoursMatch ? parseInt(hoursMatch[1]) : 0;
  const minutes = minutesMatch ? parseInt(minutesMatch[1]) : 0;
  
  return hours * 60 + minutes;
};

// Filtering logic
const filteredRecipes = recipes.filter((recipe) => {
    const matchesSearch = recipe.title
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
  
    const matchesFavorite = !showFavoritesOnly || recipe.favorite;
  
    // Tag filtering logic (AND logic - must have ALL selected tags)
    const matchesTags = selectedTags.length === 0 || 
      selectedTags.every(selectedTag => 
        (recipe.tags || []).some(t => (typeof t === 'string' ? t : t.name) === selectedTag)
      );
  
    // Time filtering logic
    const matchesTime = (() => {
      if (!selectedTime) return true;
      
      const totalMinutes = parseTimeToMinutes(recipe.total_time);
      
      switch (selectedTime) {
        case "quick":
          return totalMinutes > 0 && totalMinutes < 30;
        case "medium":
          return totalMinutes >= 30 && totalMinutes <= 60;
        case "long":
          return totalMinutes > 60;
        default:
          return true;
      }
    })();
  
    return matchesSearch && matchesFavorite && matchesTags && matchesTime;
  });

  // Load more handler
  const handleLoadMore = () => {
    const loadMoreCount = isMobile ? 10 : 20;
    setVisibleCount((prev) => prev + loadMoreCount);
  };

  const handleCardClick = (slug) =>{
    setNavOrigin('/MyRecipes')
    navigate(`/recipe/${slug}`)
  }

  const handleRemoveTag = (tagToRemove) => {
    setSelectedTags(selectedTags.filter(tag => tag !== tagToRemove));
  };

  return (
    <div className="myrecipes-container">
      <div className="myrecipes-hero" style={getHeroImageStyle()}>
        <h1>My Recipes</h1>
        <p>Discover and manage your favorite recipes</p>
      </div>
      <PillNav />
      <BottomNav />
      <div className="myrecipes-content">
        <h1 className="myrecipes-title">My Recipes</h1>

        {/* Search Bar */}
        <input
          type="text"
          placeholder="Search recipes by title..."
          className="myrecipes-search"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        {/* Filters */}
        <div className="myrecipes-filters">
          <div className="filter-buttons-wrapper">
            <label className="myrecipes-heart-checkbox-label">
              <input
                type="checkbox"
                checked={showFavoritesOnly}
                onChange={() => setShowFavoritesOnly((f) => !f)}
              />
              <svg className="heart-icon" viewBox="0 0 24 24">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
              <span>Favorites only</span>
            </label>

            <MultiTagDropdown
                options={allTags}
                selected={selectedTags}
                onChange={setSelectedTags}
                />
            <TimeDropdown
                selected={selectedTime}
                onChange={setSelectedTime}
                />
          </div>
          <TagPills
              tags={selectedTags}
              onRemoveTag={handleRemoveTag}
              />
        </div>

        {/* Debug info 
        <div style={{ padding: '20px', color: '#666' }}>
          <p>Total recipes: {recipes.length}</p>
          <p>Filtered recipes: {filteredRecipes.length}</p>
          <p>Visible recipes: {Math.min(filteredRecipes.length, visibleCount)}</p>
        </div>*/}

        {/* Recipes Grid */}
        <div className="recipes-grid">
          {filteredRecipes.length === 0 ? (
            <div className="no-recipes-message">
                           {(() => {
                 const filters = [];
                 if (showFavoritesOnly) filters.push("favorites");
                 if (selectedTags.length > 0) {
                   if (selectedTags.length === 1) {
                     filters.push(`"${selectedTags[0]}" tag`);
                   } else {
                     filters.push(`${selectedTags.length} tags (${selectedTags.join(", ")})`);
                   }
                 }
                 if (selectedTime) {
                   const timeLabels = {
                     "quick": "quick (< 30 min)",
                     "medium": "medium (30-60 min)", 
                     "long": "long (> 60 min)"
                   };
                   filters.push(timeLabels[selectedTime] || selectedTime);
                 }
                 if (searchQuery) filters.push(`"${searchQuery}" search`);
                 
                 if (filters.length === 0) {
                   return <p>No recipes found</p>;
                 } else if (filters.length === 1) {
                   return <p>No recipes found for {filters[0]}</p>;
                 } else {
                   return <p>No recipes found for {filters.slice(0, -1).join(", ")} and {filters[filters.length - 1]}</p>;
                 }
               })()}
            </div>
          ) : (
            filteredRecipes.slice(0, visibleCount).map((recipe) => (
              <CookBookCard key={recipe.slug} recipe={recipe} onClick={() => handleCardClick(recipe.slug)}/>
            ))
          )}
        </div>

        {/* Load More Button */}
        {filteredRecipes.length > visibleCount && (
          <div className="load-more-container">
            <button className="load-more-button" onClick={handleLoadMore}>
              Load More ({filteredRecipes.length - visibleCount} remaining)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
