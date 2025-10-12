
const API_URL = process.env.REACT_APP_BACKEND_URL;

export async function fetchPosts() {
    const res = await fetch(`${API_URL}/posts/`);
    return res.json();
}
