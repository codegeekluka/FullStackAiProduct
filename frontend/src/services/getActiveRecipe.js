import axios from "axios";
import { API_BASE_URL } from "../config/api";

export async function getActiveRecipe(token) {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/user/active-recipe`,
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
