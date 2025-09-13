import axios from "axios";

export async function getUserTags(token) {
  const res = await axios.get("http://localhost:8000/user/tags", {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return res.data;
}

export async function addUserTag(tagName, token) {
  const res = await axios.post(
    "http://localhost:8000/user/tags",
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
    `http://localhost:8000/user/tags/${encodeURIComponent(tagName)}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }
  );
  return res.data;
}
