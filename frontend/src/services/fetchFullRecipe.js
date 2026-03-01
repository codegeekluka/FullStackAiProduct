import axios from "axios";
import { API_BASE_URL } from "../config/api";

/**
 * Fetch a recipe from the API by slug
 * @param {string} slug - The recipe slug
 * @returns {Promise<object>} The recipe data
 */
export async function fetchFullRecipe(slug) {
  const start = Date.now();

  const res = await axios.get(`${API_BASE_URL}/recipes/${slug}`);
  // Optional: keep your artificial delay for smooth loading animations
  const elapsed = Date.now() - start;
  const delay = Math.max(0, 2000 - elapsed);

  return new Promise((resolve) => {
    setTimeout(() => resolve(res.data), delay);
  });
}
