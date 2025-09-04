import React from "react";
import { motion } from "framer-motion";
import { FaShieldAlt, FaHeartbeat, FaEye, FaUsers } from "react-icons/fa";

const iconMap = {
  "Positive Sentiment": FaShieldAlt,
  "Healthy Usage": FaHeartbeat,
  "Privacy Awareness": FaEye,
  "Respectful Interactions": FaUsers,
};

export default function InsightCard({ title, value, rating }) {
  const Icon = iconMap[title] || FaShieldAlt;
  const isLoading = value === "0%";

  return (
    <motion.div
      whileHover={{ scale: 1.06 }}
      whileTap={{ scale: 0.98 }}
      className="relative bg-gradient-to-br from-gray-900 to-gray-800 shadow-xl rounded-3xl p-6 text-center border border-gray-700 hover:border-indigo-400 transition duration-300 overflow-hidden"
    >
      {isLoading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-6 bg-gray-700 rounded w-1/2 mx-auto"></div>
          <div className="h-4 bg-gray-600 rounded w-3/4 mx-auto"></div>
        </div>
      ) : (
        <>
          {/* Icon with subtle hover animation */}
          <motion.div
            initial={{ opacity: 0, scale: 0.6, rotate: -10 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            whileHover={{ rotate: 10, scale: 1.1 }}
            transition={{ duration: 0.5, type: "spring", stiffness: 150 }}
            className="flex justify-center mb-3"
          >
            <Icon className="text-indigo-400 text-5xl drop-shadow-lg" />
          </motion.div>

          {/* Value with glow effect */}
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-extrabold text-white drop-shadow-md"
          >
            {value}
          </motion.p>

          <motion.h4
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg font-semibold text-indigo-300 mt-2"
          >
            {title}
          </motion.h4>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-sm text-gray-400 italic"
          >
            {rating}
          </motion.p>
        </>
      )}

      {/* Animated background glow overlay */}
      <motion.div
        animate={{ rotate: [0, 5, 0, -5, 0] }}
        transition={{ repeat: Infinity, duration: 10, ease: "linear" }}
        className="absolute inset-0 rounded-3xl bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-pink-500/20 blur-3xl pointer-events-none"
      ></motion.div>

      {/* Inner subtle overlay for depth */}
      <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/10 pointer-events-none"></div>
    </motion.div>
  );
}
