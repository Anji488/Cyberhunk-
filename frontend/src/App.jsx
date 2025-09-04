// File: src/App.jsx
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Cookies from "js-cookie";

import Login from "@/pages/Login";
import DashboardPage from "@/pages/DashboardPage";
import ChartsPage from "@/pages/ChartsPage";
import PostsPage from "@/pages/PostsPage";
import NotFound from "@/pages/NotFound";
import Layout from "@/components/Layout";
import AuthCallback from "@/pages/AuthCallback";
import { InsightsProvider } from "@/context/InsightsContext";

// ✅ Loading screen
function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-950 text-gray-200">
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-indigo-500 border-opacity-75"></div>
      <span className="ml-4 text-lg font-semibold">Checking authentication...</span>
    </div>
  );
}

// ✅ ProtectedRoute
function ProtectedRoute({ children }) {
  const [loading, setLoading] = useState(true);
  const [isAuthed, setIsAuthed] = useState(false);

  useEffect(() => {
    const token = Cookies.get("fb_token");
    if (token) {
      setIsAuthed(true);
    }
    setLoading(false);
  }, []);

  if (loading) return <LoadingScreen />;
  if (!isAuthed) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Router>
      <InsightsProvider>
        <Routes>
          {/* Public */}
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/auth/callback" element={<AuthCallback />} />

          {/* Protected */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/charts"
            element={
              <ProtectedRoute>
                <Layout>
                  <ChartsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/posts"
            element={
              <ProtectedRoute>
                <Layout>
                  <PostsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </InsightsProvider>
    </Router>
  );
}
