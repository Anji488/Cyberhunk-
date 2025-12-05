import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Cookies from "js-cookie";

import Login from "@/pages/Login";
import Home from "@/pages/Home";
import DashboardPage from "@/pages/DashboardPage";
import ChartsPage from "@/pages/ChartsPage";
import PostsPage from "@/pages/PostsPage";
import ProfilePage from "@/pages/Profile";

import NotFound from "@/pages/NotFound";
import Layout from "@/components/Layout";
import AuthCallback from "@/pages/AuthCallback";
import { InsightsProvider } from "@/context/InsightsContext";
import { AuthProvider } from "@/context/AuthContext"; 

import Reports from "./pages/Reports";

import About from "@/pages/About";
import Features from "@/pages/Features";
import Framework from "@/pages/OurFramework";
import PrivacyPolicy from "@/pages/Privacy";
import Terms from "@/pages/Terms";

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-950 text-gray-200">
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-indigo-500 border-opacity-75"></div>
      <span className="ml-4 text-lg font-semibold">Checking authentication...</span>
    </div>
  );
}

function ProtectedRoute({ children }) {
  const [loading, setLoading] = useState(true);
  const [isAuthed, setIsAuthed] = useState(false);

  useEffect(() => {
    const token = Cookies.get("fb_token");
    if (token) setIsAuthed(true);
    setLoading(false);
  }, []);

  if (loading) return <LoadingScreen />;
  if (!isAuthed) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <InsightsProvider>
        <Routes>
          <Route path="/" element={<Layout><Home /></Layout>} />
          <Route path="/login" element={<Layout><Login /></Layout>} />
          <Route path="/auth/callback" element={<Layout><AuthCallback /></Layout>} />
          <Route path="/about" element={<Layout><About /></Layout>} />
          <Route path="/features" element={<Layout><Features /></Layout>} />
          <Route path="/our-framework" element={<Layout><Framework /></Layout>} />
          <Route path="/terms" element={<Layout><Terms /></Layout>} />
          <Route path="/privacy-policy" element={<Layout><PrivacyPolicy /></Layout>} />

          <Route path="/dashboard" element={<ProtectedRoute><Layout><DashboardPage /></Layout></ProtectedRoute>} />
          <Route path="/charts" element={<ProtectedRoute><Layout><ChartsPage /></Layout></ProtectedRoute>} />
          <Route path="/posts" element={<ProtectedRoute><Layout><PostsPage /></Layout></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Layout><ProfilePage /></Layout></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><Layout><Reports/></Layout></ProtectedRoute>}/>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </InsightsProvider>
    </AuthProvider>
  );
}
