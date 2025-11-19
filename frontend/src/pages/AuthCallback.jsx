import React, { useEffect, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";
import { AuthContext } from "../context/AuthContext";

export default function AuthCallback() {
  const navigate = useNavigate();
  const { updateToken } = useContext(AuthContext);
  const [status, setStatus] = useState("authenticating");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");

    if (tokenFromUrl) {
      updateToken(tokenFromUrl);  // ✅ Save token in context & cookie
      Cookies.remove("fb_insights");

      window.history.replaceState({}, document.title, "/dashboard");
      navigate("/dashboard", { replace: true });
    } else {
      setStatus("failed");
      setTimeout(() => navigate("/login", { replace: true }), 2000);
    }
  }, [navigate, updateToken]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-950 text-gray-200">
      <div className="text-center">
        {status === "authenticating" ? (
          <>
            <p className="text-xl font-semibold">Authenticating...</p>
            <p className="text-gray-400 mt-2">Please wait while we log you in.</p>
            <div className="mt-6 animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-500 border-opacity-75 mx-auto"></div>
          </>
        ) : (
          <>
            <p className="text-xl font-semibold text-red-500">Authentication Failed</p>
            <p className="text-gray-400 mt-2">
              Unable to retrieve token. Please try logging in again.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
