import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FaShieldAlt, FaHeartbeat, FaEye, FaUsers } from "react-icons/fa";

const iconMap = {
  "Happy Posts": { icon: FaShieldAlt, color: "#34D399" }, 
  "Good Posting Habits": { icon: FaHeartbeat, color: "#F472B6" }, 
  "Privacy Care": { icon: FaEye, color: "#6366F1" }, 
  "Being Respectful": { icon: FaUsers, color: "#FBBF24" }, 
};

export default function InsightCard({ title, value, rating }) {
  const { icon: Icon, color } = iconMap[title] || { icon: FaShieldAlt, color: "#9CA3AF" }; 
  const targetValue = parseInt(value.replace("%", ""), 10) || 0;

  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let start = 0;
    const step = () => {
      start += Math.ceil(targetValue / 30);
      if (start >= targetValue) start = targetValue;
      setDisplayValue(start);
      if (start < targetValue) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [targetValue]);

  const size = 140;
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayValue / 100) * circumference;

  return (
    <div className="flex flex-col items-center bg-white rounded-3xl shadow-lg p-6 relative hover:scale-105 transition-transform duration-300">
     
      <div className="relative w-[140px] h-[140px] flex items-center justify-center">
        <svg width={size} height={size} className="-rotate-90">
   
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#E5E7EB"
            strokeWidth={strokeWidth}
            fill="none"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: "stroke-dashoffset 1s ease-out" }}
          />
        </svg>
        <Icon className={`absolute text-4xl`} style={{ color }} />
      </div>

      <p className="mt-3 text-3xl font-extrabold text-gray-800">{displayValue}%</p>

      <h4 className="text-lg font-semibold text-gray-700 mt-2 text-center">{title}</h4>

      <p className="text-sm text-gray-500 italic mt-1">{rating}</p>
    </div>
  );
}
