import React from "react";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { CheckCircle, AlertCircle, Shield, Moon, Sun, Heart } from "lucide-react";
import AnalyzeToken from "@/components/AnalyzeToken";
import InsightCard from "@/components/InsightCard";
import { useInsights } from "@/context/InsightsContext";

const ICONS = [CheckCircle, AlertCircle, Shield, Moon, Sun, Heart];

export default function DashboardPage() {
  const { insightsData, setInsightsData } = useInsights();
  const {
    insights = [],
    insightMetrics = [],
    recommendations = [],
    profile,
    totalPosts = 0,
    totalComments = 0
  } = insightsData;

  const total = insights.length || 1;
  const token = Cookies.get("fb_token");
  if (!token) {
    navigate("/login");
    return null;
  }


  const score = insightMetrics.reduce((sum, m) => sum + m.value, 0) / (insightMetrics.length || 1);
  let bannerText = "Good Digital Behavior";
  let bannerColor = "bg-green-400";
  if (score < 40) {
    bannerText = "Needs Attention";
    bannerColor = "bg-red-400";
  }else if (score < 60) {
    bannerText = "Needs Attention";
    bannerColor = "bg-yellow-400";
  }else if (score < 60) {
    bannerText = "Medium Behavior";
    bannerColor = "bg-pink-400";
  } else if (score < 80) {
    bannerText = "Average Behavior";
    bannerColor = "bg-blue-400";
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
 
      {profile && (
        <div className={`${bannerColor} rounded-3xl p-6 flex justify-between items-center shadow-lg`}>
          <div>
            <h2 className="text-3xl font-bold text-white drop-shadow-lg">{bannerText}</h2>
            <p className="text-white/90 mt-1">Your Facebook activity analyzed in real-time</p>
          </div>
          <div className="flex items-center bg-white p-4 rounded-2xl shadow-md">
            <img
              src={profile.picture?.data?.url}
              alt="Profile"
              className="rounded-full w-20 h-20 mr-4 border-2 border-gray-200"
            />
            <div>
              <p className="font-semibold text-gray-800">{profile.name}</p>
              <p className="text-gray-500 text-sm">{profile.gender || "N/A"}</p>
              <p className="text-gray-500 text-sm">{profile.birthday || "N/A"}</p>
            </div>
          </div>
        </div>
      )}

      {!token && (
        <p className="text-center text-red-500 mb-6 font-semibold animate-pulse">
          Facebook token not found. Please login first.
        </p>
      )}

      {token && insights.length === 0 && (
        <AnalyzeToken token={token} method="ml" onInsightsFetched={setInsightsData} />
      )}

      <motion.div
        className="flex justify-around bg-white rounded-2xl shadow-md p-6 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <p className="text-2xl font-bold text-indigo-500">{totalPosts}</p>
          <p className="text-gray-500">Posts</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-pink-500">{totalComments}</p>
          <p className="text-gray-500">Comments</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-green-500">{total}</p>
          <p className="text-gray-500">Interactions</p>
        </div>
      </motion.div>

      {/* Insight Metrics */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        initial="hidden"
        animate="visible"
        variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.15 } } }}
      >
        {insightMetrics.map((metric, idx) => (
          <InsightCard
            key={idx}
            title={metric.title}
            value={`${metric.value}%`}
            rating={metric.rating || ""}
            className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl shadow-lg hover:shadow-xl p-5 transition"
          />
        ))}
      </motion.div>

      <div>
        <h3 className="text-3xl font-bold mb-5 text-indigo-400">Personalized Recommendations</h3>
        <p>{recommendations}</p>
      </div>
    </div>
  );
}
