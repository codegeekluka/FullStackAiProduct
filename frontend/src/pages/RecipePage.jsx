import { useParams } from 'react-router-dom';
import { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import '../styles/recipes/RecipePage.css'
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import RecipeHero from '../components/pages/RecipeHero.jsx';

import { saveRecipeService } from '../services/saveRecipe.js';
import { fetchFullRecipe } from '../services/fetchFullRecipe.js';
import { updateTags } from '../services/tagsManger.js';

const RecipePage = () => {
    const { slug } = useParams();
    const { recipes } = useContext(AuthContext);
    const [recipe, setRecipe] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("instructions");
    const [draftRecipe, setDraftRecipe] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [tags, setTags] = useState([])
    const [initialRecipe, setInitialRecipe] = useState(false);
    const token = localStorage.getItem('token');

    const navigate=useNavigate()

    // Helper function to format time from hours and minutes
    const formatTime = (hours, minutes) => {
        // Convert to strings for consistent comparison
        const hoursStr = hours?.toString() || "";
        const minutesStr = minutes?.toString() || "";
        
        // If both are empty, return null
        if (!hoursStr && !minutesStr) return null;
        
        // If both have values
        if (hoursStr && minutesStr) {
            // Don't show hours if it's 0
            if (hoursStr === "0") return `${minutesStr}m`;
            return `${hoursStr}h ${minutesStr}m`;
        }
        
        // If only hours has a value (and it's not 0)
        if (hoursStr && hoursStr !== "0") return `${hoursStr}h`;
        
        // If only minutes has a value
        if (minutesStr) return `${minutesStr}m`;
        
        return null;
    };

    // Helper function to calculate total time from prep and cook times
    const calculateTotalTime = (prepHours, prepMinutes, cookHours, cookMinutes) => {
        const prepTotal = (parseInt(prepHours) || 0) * 60 + (parseInt(prepMinutes) || 0);
        const cookTotal = (parseInt(cookHours) || 0) * 60 + (parseInt(cookMinutes) || 0);
        const totalMinutes = prepTotal + cookTotal;
        
        if (totalMinutes === 0) return null;
        
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        
        if (hours === 0) return `${minutes}m`;
        if (minutes === 0) return `${hours}h`;
        return `${hours}h ${minutes}m`;
    };

    // Helper function to parse time string into hours and minutes
    const parseTime = (timeString) => {
        if (!timeString) return { hours: "", minutes: "" };
        
        const hoursMatch = timeString.match(/(\d+)h/);
        const minutesMatch = timeString.match(/(\d+)m/);
        
        return {
            hours: hoursMatch ? hoursMatch[1] : "",
            minutes: minutesMatch ? minutesMatch[1] : ""
        };
    };

    const emptyRecipeTemplate = {
        slug: "new",
        image: "",  // or placeholder image URL
        title: "Recipe title",
        description: "Recipe description",
        ingredients: ["Ingredient 1"],      // start with one blank item
        instructions: ["Step 1"],     // start with one blank item
        favorite: false,
        is_active: false,
        tags: [],
        prep_time: null,
        cook_time: null,
        total_time: null,
        prep_hours: "",
        prep_minutes: "",
        cook_hours: "",
        cook_minutes: "",
        total_hours: "",
        total_minutes: ""
      };

    useEffect(() => {
        let isMounted = true;
        if (slug === "new") {
            // Initialize new recipe state for manual add
            setRecipe(emptyRecipeTemplate);
            setDraftRecipe(emptyRecipeTemplate);
            setEditMode(true);
            setLoading(false);
            setInitialRecipe(true)
            return;
          }

        const localRecipe = recipes.find(r => r.slug === slug);

        const loadRecipe = async () => {
          try {
            setLoading(true);
            const fullRecipe= await fetchFullRecipe(slug)
        
            if (isMounted) {
                setRecipe(fullRecipe);
                
                // Parse times for editing
                const prepTime = parseTime(fullRecipe.prep_time);
                const cookTime = parseTime(fullRecipe.cook_time);
                const totalTime = parseTime(fullRecipe.total_time);
                
                setDraftRecipe({
                    ...fullRecipe,
                    prep_hours: prepTime.hours,
                    prep_minutes: prepTime.minutes,
                    cook_hours: cookTime.hours,
                    cook_minutes: cookTime.minutes,
                    total_hours: totalTime.hours,
                    total_minutes: totalTime.minutes
                });
                setTags(fullRecipe.tags || []);
                setLoading(false);
            }
          } catch (err) {
            console.error("Failed to fetch recipe:", err);
            if (isMounted) setLoading(false);
          }
        };
      
        if(localRecipe){
          setRecipe(localRecipe); // show immediate content
          
          // Parse times for editing
          const prepTime = parseTime(localRecipe.prep_time);
          const cookTime = parseTime(localRecipe.cook_time);
          const totalTime = parseTime(localRecipe.total_time);
          
          setDraftRecipe({
            ...localRecipe,
            prep_hours: prepTime.hours,
            prep_minutes: prepTime.minutes,
            cook_hours: cookTime.hours,
            cook_minutes: cookTime.minutes,
            total_hours: totalTime.hours,
            total_minutes: totalTime.minutes
          });
          setTags(localRecipe.tags || [])
        }
        loadRecipe()
        return () => {
          isMounted = false;
        };
      }, [slug, recipes]);

      const handleAddTag = async (newTag) => {
        // Handle both single tags and arrays of tags
        const tagsToAdd = Array.isArray(newTag) ? newTag : [newTag];
        const updatedTags = [...tags, ...tagsToAdd];
        setTags(updatedTags);
    
        try {
            await updateTags(recipe.slug, updatedTags, token);
          } catch (err) {
            if (err.response?.status === 403) {
              alert("Session expired. Please login again.");
              navigate('/');
            } else {
              alert("Failed to save tags");
            }
            setTags(tags); // revert on error
          }
      };
    
      const handleRemoveTag = async (tagToRemove) => {
        const updatedTags = tags.filter(t => t !== tagToRemove);
        setTags(updatedTags);
    
        try {
            await updateTags(recipe.slug, updatedTags, token);
          } catch (err) {
            if (err.response?.status === 403) {
              alert("Session expired. Please login again.");
              navigate('/');
            } else {
              alert("Failed to save tags");
            }
            setTags(tags); // revert on error
          }
      };
      
      const startEditing = () => setEditMode(true);
      
      const cancelEditing = () => {
        setDraftRecipe(recipe);
        setEditMode(false);
      };
      
      const saveRecipe = async () => {
        try {
            // Build the update payload only with defined fields
              console.log(draftRecipe)
              const savedRecipe = await saveRecipeService(draftRecipe, slug, token)
              if (savedRecipe && savedRecipe.slug) {
                setRecipe(draftRecipe);
                setEditMode(false);
                setInitialRecipe(false);
          
                if (slug === "new") {
                  navigate(`/recipe/${savedRecipe.slug}`);
                }
              }
          
        } catch (err) {
            if(err.response?.status===403){
                alert("Session expired. Please login again")
                navigate('/')
            } else{
                alert("Error saving recipe.");
            }    
        }
      };
      
      if (loading) return (
        <div className="loader-container">
            <LoadingSpinner />
        </div>
      ) 
      if (!recipe) return <div>Recipe not found</div>;

    return (
        <div className="recipe-container">
            {/* HEADER IMAGE */}
            <RecipeHero
              recipe={recipe}
              tags={tags}
              onAddTag={handleAddTag}
              onRemoveTag={handleRemoveTag}
              editMode={editMode}
              startEditing={startEditing}
              saveRecipe={saveRecipe}
              cancelEditing={cancelEditing}
              navigate={navigate}
              initialRecipe={initialRecipe}
            />

            {/* RECIPE CONTENT */}
            <div className="recipe-content">
                {editMode ? (
                    <input
                        className="recipe-input"
                        value={draftRecipe?.title || ""}
                        onChange={(e) =>
                        setDraftRecipe({ ...draftRecipe, title: e.target.value })
                        }
                    />
                    ) : (
                    <h1>{recipe?.title}</h1>
                )}
            
                {editMode ? (
                    <textarea
                        className="recipe-textarea"
                        value={draftRecipe?.description || ""}
                        onChange={(e) =>
                        setDraftRecipe({ ...draftRecipe, description: e.target.value })
                        }
                    />
                    ) : (
                    <p className="description-recipe">{recipe?.description}</p>
                )}

                {/* COOKING TIMES */}
                {editMode ? (
                    <div className="cooking-times-edit">
                        <div className="time-edit-card">
                            <svg className="time-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12,6 12,12 16,14"/>
                            </svg>
                            <div className="time-label">Prep Time</div>
                            <div className="time-inputs">
                                <input
                                    type="number"
                                    placeholder="0"
                                    min="0"
                                    value={draftRecipe?.prep_hours || ""}
                                    onChange={(e) => {
                                        const hours = e.target.value;
                                        const minutes = draftRecipe?.prep_minutes || "";
                                        const totalTime = formatTime(hours, minutes);
                                        const calculatedTotalTime = calculateTotalTime(
                                            hours, 
                                            minutes, 
                                            draftRecipe?.cook_hours || "", 
                                            draftRecipe?.cook_minutes || ""
                                        );
                                        setDraftRecipe({ 
                                            ...draftRecipe, 
                                            prep_hours: hours,
                                            prep_time: totalTime,
                                            total_time: calculatedTotalTime
                                        });
                                    }}
                                    className="time-input"
                                />
                                <span>h</span>
                                <input
                                    type="number"
                                    placeholder="0"
                                    min="0"
                                    value={draftRecipe?.prep_minutes || ""}
                                    onChange={(e) => {
                                        const minutes = e.target.value;
                                        const hours = draftRecipe?.prep_hours || "";
                                        const totalTime = formatTime(hours, minutes);
                                        const calculatedTotalTime = calculateTotalTime(
                                            hours, 
                                            minutes, 
                                            draftRecipe?.cook_hours || "", 
                                            draftRecipe?.cook_minutes || ""
                                        );
                                        setDraftRecipe({ 
                                            ...draftRecipe, 
                                            prep_minutes: minutes,
                                            prep_time: totalTime,
                                            total_time: calculatedTotalTime
                                        });
                                    }}
                                    className="time-input"
                                />
                                <span>m</span>
                            </div>
                        </div>
                        <div className="time-edit-card">
                            <svg className="time-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M9 12l2 2 4-4"/>
                                <path d="M21 12c-1 0-2-1-2-2s1-2 2-2 2 1 2 2-1 2-2 2z"/>
                                <path d="M3 12c1 0 2-1 2-2s-1-2-2-2-2 1-2 2 1 2 2 2z"/>
                                <path d="M12 3c0 1-1 2-2 2s-2-1-2-2 1-2 2-2 2 1 2 2z"/>
                                <path d="M12 21c0-1 1-2 2-2s2 1 2 2-1 2-2 2-2-1-2-2z"/>
                            </svg>
                            <div className="time-label">Cook Time</div>
                            <div className="time-inputs">
                                <input
                                    type="number"
                                    placeholder="0"
                                    min="0"
                                    value={draftRecipe?.cook_hours || ""}
                                    onChange={(e) => {
                                        const hours = e.target.value;
                                        const minutes = draftRecipe?.cook_minutes || "";
                                        const totalTime = formatTime(hours, minutes);
                                        const calculatedTotalTime = calculateTotalTime(
                                            draftRecipe?.prep_hours || "", 
                                            draftRecipe?.prep_minutes || "",
                                            hours, 
                                            minutes
                                        );
                                        setDraftRecipe({ 
                                            ...draftRecipe, 
                                            cook_hours: hours,
                                            cook_time: totalTime,
                                            total_time: calculatedTotalTime
                                        });
                                    }}
                                    className="time-input"
                                />
                                <span>h</span>
                                <input
                                    type="number"
                                    placeholder="0"
                                    min="0"
                                    value={draftRecipe?.cook_minutes || ""}
                                    onChange={(e) => {
                                        const minutes = e.target.value;
                                        const hours = draftRecipe?.cook_hours || "";
                                        const totalTime = formatTime(hours, minutes);
                                        const calculatedTotalTime = calculateTotalTime(
                                            draftRecipe?.prep_hours || "", 
                                            draftRecipe?.prep_minutes || "",
                                            hours, 
                                            minutes
                                        );
                                        setDraftRecipe({ 
                                            ...draftRecipe, 
                                            cook_minutes: minutes,
                                            cook_time: totalTime,
                                            total_time: calculatedTotalTime
                                        });
                                    }}
                                    className="time-input"
                                />
                                <span>m</span>
                            </div>
                        </div>
                        <div className="time-edit-card">
                            <svg className="time-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12,6 12,12 16,14"/>
                                <line x1="12" y1="12" x2="12" y2="6"/>
                            </svg>
                            <div className="time-label">Total Time</div>
                            <div className="time-value">{draftRecipe?.total_time || "N/A"}</div>
                        </div>
                    </div>
                ) : (
                    <div className="cooking-times">
                        <div className="time-card">
                            <svg className="time-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12,6 12,12 16,14"/>
                            </svg>
                            <div className="time-label">Prep Time</div>
                            <div className="time-value">{recipe?.prep_time || "N/A"}</div>
                        </div>
                        <div className="time-card">
                            <svg className="time-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M9 12l2 2 4-4"/>
                                <path d="M21 12c-1 0-2-1-2-2s1-2 2-2 2 1 2 2-1 2-2 2z"/>
                                <path d="M3 12c1 0 2-1 2-2s-1-2-2-2-2 1-2 2 1 2 2 2z"/>
                                <path d="M12 3c0 1-1 2-2 2s-2-1-2-2 1-2 2-2 2 1 2 2z"/>
                                <path d="M12 21c0-1 1-2 2-2s2 1 2 2-1 2-2 2-2-1-2-2z"/>
                            </svg>
                            <div className="time-label">Cook Time</div>
                            <div className="time-value">{recipe?.cook_time || "N/A"}</div>
                        </div>
                        <div className="time-card">
                            <svg className="time-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10"/>
                                <polyline points="12,6 12,12 16,14"/>
                                <line x1="12" y1="12" x2="12" y2="6"/>
                            </svg>
                            <div className="time-label">Total Time</div>
                            <div className="time-value">{recipe?.total_time || "N/A"}</div>
                        </div>
                    </div>
                )}

                {/* SLIDER / TABS */}
                <div className="tabs">
                <button
                    className={activeTab === "ingredients" ? "active" : ""}
                    onClick={() => setActiveTab("ingredients")}
                >
                    Ingredients
                </button>
                <button
                    className={activeTab === "instructions" ? "active" : ""}
                    onClick={() => setActiveTab("instructions")}
                >
                    Instructions
                </button>
                </div>

                {/* TAB CONTENT */}
                <div className="tab-content">
                {activeTab === "ingredients" && (
                    editMode ? (
                        draftRecipe?.ingredients.map((item, index) => (
                          <input
                            className="ingredients-input"
                            key={index}
                            value={item}
                            onChange={(e) => {
                              const updated = [...draftRecipe.ingredients];
                              updated[index] = e.target.value;
                              setDraftRecipe({ ...draftRecipe, ingredients: updated });
                            }}
                          />
                        ))
                      ) : (
                        <ul>
                          {recipe?.ingredients.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ul>
                      )
                      
                )}
                {activeTab === "instructions" && (
                    editMode ? (
                        draftRecipe?.instructions.map((item, index) => (
                          <textarea
                            className="instructions-textarea"
                            key={index}
                            value={item}
                            onChange={(e) => {
                              const updated = [...draftRecipe.instructions];
                              updated[index] = e.target.value;
                              setDraftRecipe({ ...draftRecipe, instructions: updated });
                            }}
                          />
                        ))
                      ) : (
                        <ol>
                          {recipe?.instructions.map((item, index) => (
                            <li key={index}>{item}</li>
                          ))}
                        </ol>
                      )
                      
                )}
                </div>
            </div>
        </div>
    );
};

export default RecipePage;
