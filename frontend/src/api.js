const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchPosts() {
    const res = await fetch(`${API_URL}/posts/`);
    return res.json();
}
