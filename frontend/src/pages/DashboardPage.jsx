// File: src/pages/DashboardPage.jsx
import React from "react";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { CheckCircle, AlertCircle, Shield, Moon, Sun, Heart } from "lucide-react";
import AnalyzeToken from "@/components/AnalyzeToken";
import InsightCard from "@/components/InsightCard";
import { useInsights } from "@/context/InsightsContext";

export default function DashboardPage() {
  const { insightsData, setInsightsData } = useInsights();
  const { insights, totalPosts, totalComments, profile } = insightsData;
  const total = insights.length || 1;

  // ✅ Only fetch if no insights yet
  const token = Cookies.get("fb_token");

  // --- Metrics calculation ---
  const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
  let nightPosts = 0, locationMentions = 0, respectfulCount = 0;

  insights.forEach(item => {
    const label = (item.label || "").toLowerCase();
    if (sentimentCounts[label] !== undefined) sentimentCounts[label]++;
    if (item.timestamp && new Date(item.timestamp).getHours() >= 23) nightPosts++;
    if (item.mentions_location) locationMentions++;
    if (item.is_respectful) respectfulCount++;
  });

  const insightMetrics = [
    { title: "Positive Sentiment", value: `${Math.round((sentimentCounts.positive / total) * 100)}%`, rating: getSentimentRating(sentimentCounts.positive / total * 100) },
    { title: "Healthy Usage", value: `${Math.round(100 - (nightPosts / total) * 100)}%`, rating: getHealthyRating(100 - (nightPosts / total) * 100) },
    { title: "Privacy Awareness", value: `${Math.round(100 - (locationMentions / total) * 100)}%`, rating: getPrivacyRating(100 - (locationMentions / total) * 100) },
    { title: "Respectful Interactions", value: `${Math.round((respectfulCount / total) * 100)}%`, rating: getRespectRating((respectfulCount / total) * 100) },
  ];

  const posPercent = (sentimentCounts.positive / total) * 100;
  const healthyPercent = 100 - (nightPosts / total) * 100;
  const privacyPercent = 100 - (locationMentions / total) * 100;
  const respectPercent = (respectfulCount / total) * 100;

  const recommendations = [];
  if (posPercent >= 80) recommendations.push({ icon: CheckCircle, text: "Your interactions are highly positive." });
  else if (posPercent >= 50) recommendations.push({ icon: AlertCircle, text: "Some interactions could be more positive." });
  else recommendations.push({ icon: AlertCircle, text: "Work on improving positivity in your posts." });

  if (healthyPercent >= 80) recommendations.push({ icon: Sun, text: "Healthy posting schedule." });
  else recommendations.push({ icon: Moon, text: "Consider reducing late-night activity." });

  if (privacyPercent >= 80) recommendations.push({ icon: Shield, text: "Minimal location info shared." });
  else recommendations.push({ icon: Shield, text: "You share location frequently, adjust privacy settings." });

  if (respectPercent >= 75) recommendations.push({ icon: Heart, text: "Excellent respect in interactions." });
  else if (respectPercent >= 50) recommendations.push({ icon: AlertCircle, text: "Some comments may be disrespectful." });
  else recommendations.push({ icon: AlertCircle, text: "Improve your tone and respectfulness." });

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-4xl font-extrabold text-indigo-400 mb-6 text-center">Dashboard</h2>

      {!token && <p className="text-center text-red-500 mb-4">Facebook token not found. Please login first.</p>}

      {token && insights.length === 0 && <AnalyzeToken token={token} method="ml" onInsightsFetched={setInsightsData} />}
      {profile && (
        <div className="flex items-center bg-gray-900 p-4 rounded-lg border border-gray-700 mb-6">
          <img
              src={profile.picture?.data?.url}
              alt="Profile"
              className="rounded-full w-20 h-20 mr-4"
            />
          <div className="text-gray-200">
            <p className="font-semibold text-xl">{profile.name}</p>
            <p>Birthday: {profile.birthday || "N/A"}</p>
            <p>Gender: {profile.gender || "N/A"}</p>
          </div>
        </div>
      )}

      <div className="mt-2 text-gray-400 text-sm text-center">
        Total Posts: {totalPosts} | Total Comments: {totalComments} | Total Interactions: {total}
      </div>

      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 my-6"
        initial="hidden"
        animate="visible"
        variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.15 } } }}
      >
        {insightMetrics.map((metric, idx) => (
          <InsightCard key={idx} title={metric.title} value={metric.value} rating={metric.rating} />
        ))}
      </motion.div>

      <div className="mt-10">
        <h3 className="text-2xl font-semibold mb-4 text-indigo-300">Personalized Recommendations</h3>
        <motion.ul
          initial="hidden"
          animate="visible"
          variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }}
          className="space-y-3"
        >
          {recommendations.map((rec, idx) => {
            const Icon = rec.icon;
            return (
              <motion.li
                key={idx}
                className="flex items-center space-x-2 bg-gray-900 p-3 rounded-lg shadow-md border border-gray-700 hover:border-indigo-400 transition"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <Icon className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                <span className="text-gray-200">{rec.text}</span>
              </motion.li>
            );
          })}
        </motion.ul>
      </div>
    </div>
  );
}

function getSentimentRating(val) { return val >= 75 ? "Excellent" : val >= 50 ? "Good" : "Needs Work"; }
function getHealthyRating(val) { return val >= 80 ? "Balanced" : "Try Reducing Late Usage"; }
function getPrivacyRating(val) { return val >= 80 ? "Good" : "Watch Location Sharing"; }
function getRespectRating(val) { return val >= 75 ? "Excellent" : "Improve Respectfulness"; }
