import axios from "axios";

export async function getActiveRecipe(token) {
  try {
    const response = await axios.get(
      "http://localhost:8000/user/active-recipe",
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    return response.data.active_recipe;
  } catch (err) {
    console.error("Failed to fetch active recipe", err);
    throw err;
  }
}
