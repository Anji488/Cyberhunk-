
const API_URL = "https://spurtive-subtilely-earl.ngrok-free.dev";

export async function fetchPosts() {
    const res = await fetch(`${API_URL}/posts/`);
    return res.json();
}
