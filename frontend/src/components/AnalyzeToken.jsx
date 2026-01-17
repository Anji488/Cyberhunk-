
import React, { useEffect, useState } from "react";
import axios from "axios";
import Cookies from "js-cookie";

export default function AnalyzeToken({ token: propToken, method = "ml", onInsightsFetched }) {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState([]);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  const BACKEND_URL = "https://cyberhunk.onrender.com";

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
        const cachedData = Cookies.get("fb_insights");
        if (cachedData) {
          const parsed = JSON.parse(cachedData);
          console.log("✅ Using cached insights data:", parsed); 
          setProfile(parsed.profile || null);
          setInsights(parsed.insights || []);
          
          if (onInsightsFetched) onInsightsFetched(parsed);
          
          setLoading(false);
          return;
        }
      } catch (e) {
        console.warn("Malformed fb_insights cookie found. Clearing cookie and fetching new data.", e);
        Cookies.remove("fb_insights"); 
      }

      try {
        
        const res = await axios.get(`${BACKEND_URL}/insights/analyze/`, {
          params: { 
            method, 
            max_posts: 20,
            token: token
          },
          headers: { 
            Authorization: `Bearer ${token}` 
          },
          withCredentials: true,
        });


        console.log("✅ Raw backend response:", res.data);

        if (!res.data || typeof res.data !== "object" || (typeof res.data === 'string' && res.data.includes("ngrok"))) {
          console.error("Response is not JSON (likely ngrok interstitial or server error):", res.data);
          throw new Error("NGROK_ISSUE"); 
        }

        const profileData = res.data?.profile || null;
        const fetchedInsights = Array.isArray(res.data?.insights) ? res.data.insights : [];

        setProfile(profileData);
        setInsights(fetchedInsights);

        const totalPosts = fetchedInsights.filter(i => i?.type === "post").length;
        const totalComments = fetchedInsights.filter(i => i?.type === "comment").length; 

        const finalData = {
          profile: profileData,
          insights: fetchedInsights,
          totalPosts,
          totalComments,
          insightMetrics: res.data?.insightMetrics || [],
          recommendations: res.data?.recommendations || []
        };

        console.log("✅ Processed insights data (finalData):", finalData);

        Cookies.set("fb_insights", JSON.stringify(finalData), {
          expires: 1, 
          sameSite: "Lax",
          secure: window.location.protocol === "https:",
        });

        if (onInsightsFetched) onInsightsFetched(finalData);
        try {
          await axios.post(
            `${BACKEND_URL}/insights/request-report/`,
            {
              token: token,
              method,
              max_posts: 20,
            },
            { withCredentials: true }
          );
          console.log("✅ Report generation triggered");
        } catch (e) {
          console.error("Failed to trigger report generation", e);
        }
      } catch (err) {
        console.error("Token analysis failed:", err);
        const errorMessage = err.response 
          ? `Server Error: ${err.response.status}`
          : "Network/CORS Error: The backend is likely waking up or blocking the request.";
          
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [method, propToken, onInsightsFetched]); 

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-500 border-opacity-75"></div>
        <span className="ml-3 text-gray-400">Analyzing token...</span>
      </div>
    );
  }

  if (error) return <p className="text-red-500 font-medium p-4">{error}</p>;
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