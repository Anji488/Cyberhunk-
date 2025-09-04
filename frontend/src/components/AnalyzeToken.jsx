// File: src/components/AnalyzeToken.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import Cookies from "js-cookie";

export default function AnalyzeToken({ token: propToken, method = "ml", onInsightsFetched }) {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState([]);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = propToken || Cookies.get("fb_token");
    if (!token) {
      setError("Facebook token not found. Please login first.");
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      try {
        // 1️⃣ Check if cached data exists
        const cachedData = Cookies.get("fb_insights");
        if (cachedData) {
          const parsed = JSON.parse(cachedData);
          setProfile(parsed.profile || null);
          setInsights(parsed.insights || []);
          if (onInsightsFetched) onInsightsFetched(parsed);
          setLoading(false);
          return; // already loaded from cache
        }

        // 2️⃣ Fetch profile from FB Graph
        const profileRes = await axios.get(
          `https://graph.facebook.com/me?fields=id,name,birthday,gender,picture.width(150).height(150)&access_token=${token}`
        );
        setProfile(profileRes.data);

        // 3️⃣ Fetch insights from backend
        const res = await axios.get(
          `http://localhost:8000/insights/analyze/?token=${token}&method=${method}`,
          { withCredentials: true }
        );

        const fetchedInsights = res.data.insights || [];
        setInsights(fetchedInsights);

        const totalPosts = fetchedInsights.filter(i => i.type === "post").length;
        const totalComments = fetchedInsights.filter(i => i.type === "comment").length;

        const finalData = {
          profile: profileRes.data,
          insights: fetchedInsights,
          totalPosts,
          totalComments,
        };

        // 4️⃣ Save to cookies for smooth reload
        Cookies.set("fb_insights", JSON.stringify(finalData), { expires: 1 }); // 1 day

        if (onInsightsFetched) onInsightsFetched(finalData);

      } catch (err) {
        console.error("Failed to fetch or analyze token", err);
        setError("Failed to fetch or analyze Facebook data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [method, propToken, onInsightsFetched]);

  if (loading) return <p className="text-gray-600">Analyzing token...</p>;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!profile) return null;

  // Display profile: left picture, right details
  return (
    <div className="flex items-center bg-gray-900 p-4 rounded-lg border border-gray-700 mb-6">
      <img
        src={profile.picture?.data?.url}
        alt="Profile"
        className="rounded-full w-20 h-20 mr-4"
      />
      <div className="text-gray-200">
        <p className="font-semibold text-lg">{profile.name}</p>
        <p className="text-sm text-gray-400">Birthday: {profile.birthday || "N/A"}</p>
        <p className="text-sm text-gray-400">Gender: {profile.gender || "N/A"}</p>
      </div>
    </div>
  );
}
