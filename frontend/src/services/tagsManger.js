import axios from "axios";
import { API_BASE_URL } from "../config/api";

export async function updateTags(slug, tags, token) {
  const res = await axios.put(
    `${API_BASE_URL}/recipe/${slug}/tags`,
    { tags }, // sending array of tags to backend
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );
  return res.data;
}
