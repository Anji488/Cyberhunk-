import React from "react";
import { motion } from "framer-motion";
import { Smile, Frown, Eye, AlertTriangle, Shield } from "lucide-react";
import { useInsights } from "@/context/InsightsContext";

export default function PostsPage() {
  const { insightsData } = useInsights();
  const { profile, insights = [] } = insightsData;

  const getSentimentIcon = (label) => {
    const map = { positive: Smile, negative: Frown, neutral: Smile };
    return map[label?.toLowerCase()] || Smile;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Page Banner */}
      <div className="bg-gradient-to-r from-indigo-100 via-pink-100 to-yellow-100 rounded-3xl p-6 shadow-lg flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-extrabold text-indigo-600 drop-shadow-sm">
            Posts & Comments
          </h2>
          <p className="mt-1 text-gray-700 font-medium">
            Explore your Facebook activity in a fun, visual way
          </p>
        </div>
        {profile && (
          <div className="flex items-center bg-white p-3 rounded-2xl shadow-md">
            <img
              src={profile.picture?.data?.url}
              alt="Profile"
              className="rounded-full w-16 h-16 mr-3 border-2 border-gray-200"
            />
            <div>
              <p className="font-semibold text-gray-800">{profile.name}</p>
              <p className="text-gray-500 text-sm">{profile.user_gender || "N/A"}</p>
            </div>
          </div>
        )}
      </div>

      {/* Posts List */}
      <div className="grid gap-4">
        {insights.length === 0 && (
          <p className="text-gray-400 text-center mt-6">
            No posts or comments found.
          </p>
        )}

        {insights.map((item, idx) => {
          const SentimentIcon = getSentimentIcon(item.label);
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
              className="bg-gradient-to-br from-indigo-50 via-pink-50 to-yellow-50 rounded-2xl shadow-lg p-5 border border-gray-200 hover:shadow-2xl transition flex flex-col gap-3"
            >
              <div className="flex items-center justify-between">
                <p className="text-gray-800 font-medium break-words">{item.original || "(empty)"}</p>
                <SentimentIcon
                  className={`w-6 h-6 flex-shrink-0 ${
                    item.label?.toLowerCase() === "positive"
                      ? "text-green-400"
                      : item.label?.toLowerCase() === "negative"
                      ? "text-red-400"
                      : "text-yellow-400"
                  }`}
                />
              </div>

              <div className="flex flex-wrap gap-3 text-sm text-gray-600 mt-1">
                <span>
                  Type: <span className="font-semibold">{item.type}</span>
                </span>
                <span>
                  Sentiment: <span className="font-semibold">{item.label}</span>
                </span>
                <span className="flex items-center">
                  Privacy: <Eye className="w-4 h-4 mr-1 text-indigo-400" />{" "}
                  {item.privacy_disclosure ? "Yes" : "No"}
                </span>
                <span className="flex items-center">
                  Toxic: <AlertTriangle className="w-4 h-4 mr-1 text-red-400" />{" "}
                  {item.toxic ? "Yes" : "No"}
                </span>
                <span className="flex items-center">
                  Location Shared: <Shield className="w-4 h-4 mr-1 text-yellow-400" />{" "}
                  {item.mentions_location ? "Yes" : "No"}
                </span>
                <span>
                  Time: {item.timestamp ? new Date(item.timestamp).toLocaleString() : "N/A"}
                </span>
                <span>
                  Respectful: <span className="font-semibold">{item.is_respectful ? "Yes" : "No"}</span>
                </span>
                <span>
                  Potential Misinformation: <span className="font-semibold">{item.misinformation_risk ? "Yes" : "No"}</span>
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
