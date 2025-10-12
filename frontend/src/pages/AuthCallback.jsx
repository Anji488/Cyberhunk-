// File: src/pages/AuthCallback.jsx
import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

export default function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      Cookies.set("fb_token", token, { expires: 7 });
      Cookies.remove("fb_insights"); // reset old cache
      navigate("/dashboard");
    } else {
      navigate("/login");
    }
  }, [navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-950 text-gray-200">
      <div className="text-center">
        <p className="text-xl font-semibold">Authenticating...</p>
        <p className="text-gray-400 mt-2">Please wait while we log you in.</p>
      </div>
    </div>
  );
}
