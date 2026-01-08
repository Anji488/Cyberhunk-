import React from "react";
import { Bar, Line, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from "chart.js";
import { motion } from "framer-motion";
import { useInsights } from "@/context/InsightsContext";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler 
);

export default function ChartsPage() {
  const { insightsData } = useInsights();
  const { profile, insights = [] } = insightsData;

  if (insights.length === 0) {
    return (
      <p className="text-center text-gray-400 mt-20 text-lg">
        No insights available yet. Please analyze on the Dashboard first.
      </p>
    );
  }

  // --- Chart data ---
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

  const pieData = {
    labels: ["Positive", "Negative", "Neutral"],
    datasets: [
      {
        data: [sentimentCounts.positive, sentimentCounts.negative, sentimentCounts.neutral],
        backgroundColor: ["#4ade80", "#f87171", "#facc15"],
        borderColor: "#f3f4f6",
        borderWidth: 2,
      },
    ],
  };

  const barData = {
    labels: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    datasets: [
      {
        label: "Posts",
        data: [0, 0, 0, 0, 0, 0, 0].map((_, idx) => postsPerDay[idx] || 0),
        backgroundColor: "#60a5fa",
        borderRadius: 8,
      },
    ],
  };

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
        pointRadius: 6,
        fill: true,
      },
    ],
  };

  const lightOptions = {
    plugins: {
      legend: {
        labels: { color: "#1f2937" },
      },
      tooltip: {
        titleColor: "#111827",
        bodyColor: "#111827",
        backgroundColor: "#f3f4f6",
        borderColor: "#e5e7eb",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: { color: "#374151" },
        grid: { color: "#e5e7eb" },
      },
      y: {
        ticks: { color: "#374151" },
        grid: { color: "#e5e7eb" },
      },
    },
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Light Modern Page Banner */}
      <div className="bg-gradient-to-r from-indigo-100 via-pink-100 to-yellow-100 rounded-3xl p-6 shadow-lg flex items-center justify-between">
        <div>
          <h2 className="text-4xl font-extrabold text-indigo-600 drop-shadow-sm">
            Insights Charts
          </h2>
          <p className="mt-1 text-gray-700 font-medium">
            Visualize your activity and engagement in an easy way
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

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <motion.div
          className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3 className="text-xl font-semibold text-indigo-500 mb-3 text-center drop-shadow-sm">
            Sentiment Distribution
          </h3>
          <Pie data={pieData} options={lightOptions} />
        </motion.div>

        <motion.div
          className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3 className="text-xl font-semibold text-indigo-500 mb-3 text-center drop-shadow-sm">
            Posts by Day
          </h3>
          <Bar data={barData} options={lightOptions} />
        </motion.div>

        <motion.div
          className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200 md:col-span-2"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3 className="text-xl font-semibold text-indigo-500 mb-3 text-center drop-shadow-sm">
            Engagement Over Weeks
          </h3>
          <Line data={lineData} options={lightOptions} />
        </motion.div>
      </div>
    </div>
  );
}
