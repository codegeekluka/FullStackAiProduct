import axios from "axios";
import { API_BASE_URL } from "../config/api";

export async function getUserTags(token) {
  const res = await axios.get(`${API_BASE_URL}/user/tags`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return res.data;
}

export async function addUserTag(tagName, token) {
  const res = await axios.post(
    `${API_BASE_URL}/user/tags`,
    { tag_name: tagName },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );
  return res.data;
}

export async function removeUserTag(tagName, token) {
  const res = await axios.delete(
    `${API_BASE_URL}/user/tags/${encodeURIComponent(tagName)}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );
  return res.data;
}
