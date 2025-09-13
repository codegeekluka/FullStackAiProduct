import axios from "axios";

export async function removeActiveRecipe(token) {
  try {
    // First get the current active recipe
    const activeRecipeResponse = await axios.get(
      "http://localhost:8000/user/active-recipe",
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    const activeRecipe = activeRecipeResponse.data.active_recipe;
    
    if (!activeRecipe) {
      throw new Error("No active recipe found");
    }
    
    // Deactivate the current active recipe
    const res = await axios.put(
      `http://localhost:8000/recipe/${activeRecipe.slug}/active`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    return res.data.is_active;
  } catch (err) {
    console.error("Failed to remove active recipe", err);
    throw err;
  }
}
