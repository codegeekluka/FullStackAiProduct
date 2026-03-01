// src/api/toggleActive.js
import axios from "axios";
import { API_BASE_URL } from "../config/api";

export async function toggleActive(slug, token) {
  try {
    const res = await axios.put(
      `${API_BASE_URL}/recipe/${slug}/active`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return res.data.is_active;
  } catch (err) {
    console.error("Failed to toggle active status", err);
    throw err;
  }
}
