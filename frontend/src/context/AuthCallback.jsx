import React, { useEffect, useContext } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function AuthCallback() {
  const { updateToken } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");

    if (token) {
      updateToken(token);      // Save token in AuthContext and cookies
      navigate("/dashboard");  // Redirect after login
    } else {
      navigate("/login");      // Redirect if no token
    }
  }, [location, updateToken, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-xl font-semibold text-gray-700">
        Logging you in, please wait...
      </p>
    </div>
  );
}
