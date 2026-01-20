import React, { useRef } from "react";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import {
  CheckCircle,
  AlertCircle,
  Shield,
  Moon,
  Sun,
  Heart,
  Share2,
  Download
} from "lucide-react";
import * as htmlToImage from "html-to-image";
import download from "downloadjs";
import { Pie, Bar, Line } from "react-chartjs-2";
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
import { useInsights } from "../context/InsightsContext";
import InsightCard from "@/components/InsightCard";

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

const ICONS = [CheckCircle, AlertCircle, Shield, Moon, Sun, Heart];

export default function ProfilePage() {
  const { insightsData } = useInsights();
  const {
    insights = [],
    insightMetrics = [],
    recommendations = [],
    profile,
    totalPosts = 0,
    totalComments = 0
  } = insightsData;

  const exportRef = useRef(null);
  const token = Cookies.get("fb_token");

  if (!token) {
    return (
      <p className="text-center text-red-500 mt-10">
        Please login to view your profile
      </p>
    );
  }

  const totalInteractions = insights.length || 1;

  const score =
    insightMetrics.reduce((sum, m) => sum + m.value, 0) /
    (insightMetrics.length || 1);

  let bannerText = "Good Digital Behavior";
  let bannerColor = "bg-green-400";

  if (score < 40) {
    bannerText = "Needs Attention";
    bannerColor = "bg-red-400";
  } else if (score < 60) {
    bannerText = "Medium Behavior";
    bannerColor = "bg-yellow-400";
  } else if (score < 80) {
    bannerText = "Average Behavior";
    bannerColor = "bg-blue-400";
  }

  //  SHARE IMAGE
  const shareImage = async () => {
    try {
      if (!exportRef.current) return;

      const dataUrl = await htmlToImage.toPng(exportRef.current);
      const blob = await (await fetch(dataUrl)).blob();
      const file = new File([blob], "profile.png", { type: blob.type });

      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: "My Digital Behavior Report",
          text: "Check out my insights!",
          files: [file]
        });
      } else {
        alert("This device does not support sharing images. Try downloading.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  // DOWNLOAD IMAGE
  const downloadImage = () => {
    if (!exportRef.current) return;
    htmlToImage
      .toPng(exportRef.current)
      .then((dataUrl) => download(dataUrl, "profile.png"))
      .catch((err) => console.error(err));
  };

  // Chart Data
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
        data: [
          sentimentCounts.positive,
          sentimentCounts.negative,
          sentimentCounts.neutral
        ],
        backgroundColor: ["#4ade80", "#f87171", "#facc15"],
        borderColor: "#f3f4f6",
        borderWidth: 2
      }
    ]
  };

  const barData = {
    labels: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    datasets: [
      {
        label: "Posts",
        data: [0, 0, 0, 0, 0, 0, 0].map((_, idx) => postsPerDay[idx] || 0),
        backgroundColor: "#60a5fa",
        borderRadius: 8
      }
    ]
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
        pointRadius: 6,
        fill: true
      }
    ]
  };

  const chartOptions = {
    plugins: {
      legend: { labels: { color: "#1f2937" } },
      tooltip: {
        backgroundColor: "#f3f4f6",
        titleColor: "#111827",
        bodyColor: "#111827",
        borderColor: "#e5e7eb",
        borderWidth: 1
      }
    },
    scales: {
      x: { ticks: { color: "#374151" }, grid: { color: "#e5e7eb" } },
      y: { ticks: { color: "#374151" }, grid: { color: "#e5e7eb" } }
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">

      {/* Buttons */}
      <div className="flex justify-end gap-3">
        <button
          onClick={shareImage}
          className="flex items-center gap-2 bg-purple-500 text-white px-4 py-2 rounded-xl shadow-lg hover:bg-purple-600"
        >
          <Share2 className="w-5 h-5" /> Share
        </button>

        <button
          onClick={downloadImage}
          className="flex items-center gap-2 bg-indigo-500 text-white px-4 py-2 rounded-xl shadow-lg hover:bg-indigo-600"
        >
          <Download className="w-5 h-5" /> Download
        </button>
      </div>

      {/* EXPORT AREA */}
      <div
        ref={exportRef}
        className="bg-white p-6 rounded-3xl shadow-xl space-y-8"
      >

        {/* Banner */}
        {profile && (
          <div
            className={`${bannerColor} rounded-3xl p-6 flex justify-between items-center shadow-lg`}
          >
            <div>
              <h2 className="text-3xl font-bold text-white drop-shadow-lg">
                {bannerText}
              </h2>
              <p className="text-white/90 mt-1">
                Your Facebook activity analyzed in real-time
              </p>
            </div>

            <div className="flex items-center bg-white p-4 rounded-2xl shadow-md">
              <img
                src={profile.picture?.data?.url}
                className="rounded-full w-20 h-20 mr-4 border-2 border-gray-200"
              />
              <div>
                <p className="font-semibold text-gray-800">{profile.name}</p>
                <p className="text-gray-500 text-sm">
                  {profile.gender || "N/A"}
                </p>
                <p className="text-gray-500 text-sm">
                  {profile.birthday || "N/A"}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Metrics */}
        <motion.div className="flex justify-around bg-gray-50 rounded-2xl shadow-md p-6 text-center">
          <div>
            <p className="text-2xl font-bold text-indigo-500">{totalPosts}</p>
            <p className="text-gray-500">Posts</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-pink-500">{totalComments}</p>
            <p className="text-gray-500">Comments</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-500">
              {totalInteractions}
            </p>
            <p className="text-gray-500">Interactions</p>
          </div>
        </motion.div>

        {/* Insight Metrics */}
        <motion.div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {insightMetrics.map((metric, idx) => (
            <InsightCard
              key={idx}
              title={metric.title}
              value={`${metric.value}%`}
              rating={metric.rating}
              className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl shadow-lg p-5"
            />
          ))}
        </motion.div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200">
            <h3 className="text-xl font-semibold text-indigo-500 mb-3 text-center">
              Sentiment Distribution
            </h3>
            <Pie data={pieData} options={chartOptions} />
          </motion.div>

          <motion.div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200">
            <h3 className="text-xl font-semibold text-indigo-500 mb-3 text-center">
              Posts by Day
            </h3>
            <Bar data={barData} options={chartOptions} />
          </motion.div>

          <motion.div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200 md:col-span-2">
            <h3 className="text-xl font-semibold text-indigo-500 mb-3 text-center">
              Engagement Over Weeks
            </h3>
            <Line data={lineData} options={chartOptions} />
          </motion.div>
        </div>

        {/* Recommendations */}
        <div>
          <h3 className="text-2xl font-bold mb-4 text-indigo-400">
            Personalized Recommendations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec, idx) => {
              const Icon = ICONS[idx % ICONS.length];
              return (
                <div
                  key={idx}
                  className="flex items-center gap-3 bg-gradient-to-br from-pink-50 to-purple-50 rounded-2xl p-4 shadow-md"
                >
                  <Icon className="w-6 h-6 text-pink-400" />
                  <span className="text-gray-700 font-medium">{rec.text}</span>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
}
