// File: src/pages/ChartsPage.jsx
import React from "react";
import { Bar, Line, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,   // needed for Line chart
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { motion } from "framer-motion";
import { useInsights } from "@/context/InsightsContext";

// Register all required chart.js elements
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function ChartsPage() {
  const { insightsData } = useInsights();
  const { profile, insights } = insightsData;

  if (!insights || insights.length === 0) {
    return (
      <p className="text-center text-gray-400 mt-20">
        No insights available yet. Please analyze on the Dashboard first.
      </p>
    );
  }

  // --- Chart data prep ---
  const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
  const postsPerDay = {};
  const engagementPerWeek = [0, 0, 0, 0];

  insights.forEach((item) => {
    const label = (item.label || "").toLowerCase();
    if (sentimentCounts[label] !== undefined) sentimentCounts[label]++;

    if (item.timestamp) {
      const date = new Date(item.timestamp);
      const day = date.getDay();
      postsPerDay[day] = (postsPerDay[day] || 0) + 1;

      const week = Math.min(Math.floor((date.getDate() - 1) / 7), 3);
      engagementPerWeek[week] += 1;
    }
  });

  // Pie chart (sentiments)
  const pieData = {
    labels: ["Positive", "Negative", "Neutral"],
    datasets: [
      {
        data: [
          sentimentCounts.positive,
          sentimentCounts.negative,
          sentimentCounts.neutral,
        ],
        backgroundColor: ["#4ade80", "#f87171", "#facc15"], // brighter dark-theme colors
        borderColor: "#1f2937",
        borderWidth: 2,
      },
    ],
  };

  // Bar chart (posts by day)
  const barData = {
    labels: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    datasets: [
      {
        label: "Posts",
        data: [0, 0, 0, 0, 0, 0, 0].map((_, idx) => postsPerDay[idx] || 0),
        backgroundColor: "#6366f1",
        borderRadius: 6,
      },
    ],
  };

  // Line chart (engagement)
  const lineData = {
    labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
    datasets: [
      {
        label: "Engagement",
        data: engagementPerWeek,
        borderColor: "#22d3ee",
        backgroundColor: "rgba(34,211,238,0.2)",
        tension: 0.4,
        pointBackgroundColor: "#22d3ee",
        pointBorderColor: "#0f172a",
        pointRadius: 5,
        fill: true,
      },
    ],
  };

  // Dark theme options for all charts
  const darkOptions = {
    plugins: {
      legend: {
        labels: { color: "#e5e7eb" },
      },
      tooltip: {
        titleColor: "#f3f4f6",
        bodyColor: "#f3f4f6",
        backgroundColor: "#1f2937",
      },
    },
    scales: {
      x: {
        ticks: { color: "#d1d5db" },
        grid: { color: "#374151" },
      },
      y: {
        ticks: { color: "#d1d5db" },
        grid: { color: "#374151" },
      },
    },
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-4xl font-extrabold text-indigo-400 mb-6 text-center">
        Distribution Charts
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <motion.div
          className="bg-gray-900 p-6 rounded-xl shadow-lg border border-gray-700"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3 className="text-xl font-semibold text-indigo-300 mb-2 text-center">
            Sentiment Distribution
          </h3>
          <Pie data={pieData} options={darkOptions} />
        </motion.div>

        <motion.div
          className="bg-gray-900 p-6 rounded-xl shadow-lg border border-gray-700"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3 className="text-xl font-semibold text-indigo-300 mb-2 text-center">
            Posts by Day
          </h3>
          <Bar data={barData} options={darkOptions} />
        </motion.div>

        <motion.div
          className="bg-gray-900 p-6 rounded-xl shadow-lg border border-gray-700 md:col-span-2"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3 className="text-xl font-semibold text-indigo-300 mb-2 text-center">
            Engagement Over Weeks
          </h3>
          <Line data={lineData} options={darkOptions} />
        </motion.div>
      </div>
    </div>
  );
}
