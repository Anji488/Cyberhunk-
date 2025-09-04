// File: src/pages/PostsPage.jsx
import React from "react";
import { motion } from "framer-motion";
import { Smile, Frown, Eye, AlertTriangle, Shield } from "lucide-react";
import { useInsights } from "@/context/InsightsContext";

export default function PostsPage() {
  const { insightsData } = useInsights();
  const { profile, insights } = insightsData;

  const getSentimentIcon = (label) => {
    const map = { positive: Smile, negative: Frown, neutral: Smile };
    return map[label?.toLowerCase()] || Smile;
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-4xl font-extrabold text-indigo-400 mb-6 text-center">
        Posts & Comments
      </h2>

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

      <div className="grid gap-4 mt-6">
        {(!insights || insights.length === 0) && (
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
              transition={{ delay: idx * 0.02 }}
              className="bg-gray-900 rounded-xl shadow-md p-4 border border-gray-700 hover:border-indigo-400 transition flex flex-col gap-2"
            >
              <div className="flex items-center justify-between">
                <p className="text-gray-200 font-medium break-words">
                  {item.original || "(empty)"}
                </p>
                <SentimentIcon className="w-5 h-5 text-green-400 flex-shrink-0" />
              </div>

              <div className="flex flex-wrap gap-3 text-sm text-gray-400 mt-1">
                <span>
                  Type: <span className="font-semibold">{item.type}</span>
                </span>
                <span>
                  Sentiment: <span className="font-semibold">{item.label}</span>
                </span>
                <span>
                  Privacy:{" "}
                  <Eye className="inline w-4 h-4 mr-1 text-indigo-400" />
                  {item.privacy_disclosure ? "Yes" : "No"}
                </span>
                <span>
                  Toxic:{" "}
                  <AlertTriangle className="inline w-4 h-4 mr-1 text-red-400" />
                  {item.toxic ? "Yes" : "No"}
                </span>
                <span>
                  Location Shared:{" "}
                  <Shield className="inline w-4 h-4 mr-1 text-yellow-400" />
                  {item.mentions_location ? "Yes" : "No"}
                </span>
                <span>
                  Time:{" "}
                  {item.timestamp
                    ? new Date(item.timestamp).toLocaleString()
                    : "N/A"}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
