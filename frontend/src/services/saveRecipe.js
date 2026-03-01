import axios from "axios";
import { API_BASE_URL } from "../config/api";

/**
 * Save a recipe to the backend.
 * - If slug === "new", it will POST a new recipe.
 * - Otherwise, it will PUT (update) the existing one.
 * @param {Object} draftRecipe - The recipe data to save
 * @param {string} slug - The recipe slug ("new" for a new recipe)
 * @param {string} token - The user's auth token
 * @returns {Promise<Object>} - The saved recipe data
 */
export async function saveRecipeService(draftRecipe, slug, token) {
  const updatePayload = {};

  if (draftRecipe.title !== undefined) updatePayload.title = draftRecipe.title;
  if (draftRecipe.image !== undefined) updatePayload.image = draftRecipe.image;
  if (draftRecipe.description !== undefined) updatePayload.description = draftRecipe.description;
  if (draftRecipe.ingredients !== undefined) updatePayload.ingredients = draftRecipe.ingredients;
  if (draftRecipe.instructions !== undefined) updatePayload.instructions = draftRecipe.instructions;
  if (draftRecipe.favorite !== undefined) updatePayload.favorite = draftRecipe.favorite;
  if (draftRecipe.is_active !== undefined) updatePayload.is_active = draftRecipe.is_active;
  if (draftRecipe.tags !== undefined) updatePayload.tags = draftRecipe.tags;
  
  console.log(draftRecipe.tags)


  const config = {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  };
  try {
    if (slug === "new") {

      const res = await axios.post(`${API_BASE_URL}/recipe/manualRecipe`, updatePayload, config);
      console.log("the error: ", res.data)
      return res.data;
    } else {
      const res = await axios.put(`${API_BASE_URL}/recipes/${slug}`, updatePayload, config);
      return res.data;
    }
  } catch(err) {
    console.log("this is the error: ", err)
  }
  
}
