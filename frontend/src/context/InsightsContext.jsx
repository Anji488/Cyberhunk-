// File: src/context/InsightsContext.jsx
import React, { createContext, useState, useContext } from "react";
import Cookies from "js-cookie";

const InsightsContext = createContext();

export function InsightsProvider({ children }) {
  const [insightsData, setInsightsData] = useState(() => {
    const cached = Cookies.get("fb_insights");
    return cached
      ? JSON.parse(cached)
      : { profile: null, insights: [], totalPosts: 0, totalComments: 0 };
  });

  return (
    <InsightsContext.Provider value={{ insightsData, setInsightsData }}>
      {children}
    </InsightsContext.Provider>
  );
}

export function useInsights() {
  return useContext(InsightsContext);
}
