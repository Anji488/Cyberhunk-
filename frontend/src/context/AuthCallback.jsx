// File: src/pages/AuthCallback.jsx
import React, { useEffect, useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";
import { AuthContext } from "../context/AuthContext";

export default function AuthCallback() {
  const navigate = useNavigate();
  const [status, setStatus] = useState("authenticating");

  const { updateToken } = useContext(AuthContext);

  useEffect(() => {
  // Clean fragment (#_=_)
  if (window.location.hash && window.location.hash === "#_=_") {
    window.history.replaceState(null, null, window.location.pathname + window.location.search);
  }

  const params = new URLSearchParams(window.location.search);
  const tokenFromUrl = params.get("token");

  if (tokenFromUrl) {
    updateToken(tokenFromUrl);

    // redirect after context is updated
    setTimeout(() => navigate("/dashboard", { replace: true }), 100); 
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
            <p className="text-gray-400 mt-2">Logging you in...</p>
            <div className="mt-6 animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-500 mx-auto"></div>
          </>
        ) : (
          <>
            <p className="text-xl font-semibold text-red-500">
              Authentication Failed
            </p>
            <p className="text-gray-400 mt-2">
              Unable to retrieve token. Try again.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
