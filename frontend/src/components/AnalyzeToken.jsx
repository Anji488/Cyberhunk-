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
        // Check for cached data
        const cachedData = Cookies.get("fb_insights");
        if (cachedData) {
          const parsed = JSON.parse(cachedData);
          setProfile(parsed.profile || null);
          setInsights(parsed.insights || []);
          if (onInsightsFetched) onInsightsFetched(parsed);
          setLoading(false);
          return;
        }

        // Fetch insights from backend
        const res = await axios.get(
          `https://cyberhunk.onrender.com/insights/analyze/?token=${token}&method=${method}`,
          { withCredentials: true }
        );

        const { profile: profileData, insights: fetchedInsights } = res.data;
        setProfile(profileData);
        setInsights(fetchedInsights || []);

        const totalPosts = fetchedInsights.filter(i => i.type === "post").length;
        const totalComments = fetchedInsights.filter(i => i.type === "comment").length;

        const finalData = {
          profile: profileData,
          insights: fetchedInsights,
          totalPosts,
          totalComments,
          insightMetrics: res.data.insightMetrics || [],
          recommendations: res.data.recommendations || []
        };

        Cookies.set("fb_insights", JSON.stringify(finalData), { expires: 1 }); // cache 1 day
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

  if (loading)
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-500 border-opacity-75"></div>
        <span className="ml-3 text-gray-400">Analyzing token...</span>
      </div>
    );

  if (error)
    return <p className="text-red-500 font-medium p-4">{error}</p>;

  if (!profile) return null;

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
