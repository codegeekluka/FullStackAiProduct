// src/api/toggleFavorite.js
import axios from "axios";
import { API_BASE_URL } from "../config/api";

export async function toggleFavorite(slug, token) {
  try {
    const res = await axios.put(
      `${API_BASE_URL}/recipe/${slug}/favorite`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return res.data.is_favorite;
  } catch (err) {
    console.error("Failed to toggle favorite", err);
    throw err;
  }
}
