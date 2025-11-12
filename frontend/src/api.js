
const API_URL = "https://https://cyberhunk.onrender.com";

export async function fetchPosts() {
    const res = await fetch(`${API_URL}/posts/`);
    return res.json();
}
