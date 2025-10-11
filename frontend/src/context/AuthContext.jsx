// File: src/context/AuthContext.jsx
import React, { createContext, useState, useEffect } from "react";
import Cookies from "js-cookie";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const savedToken = Cookies.get("fb_token");
    if (savedToken) setToken(savedToken);
  }, []);

  const updateToken = (newToken) => {
    Cookies.set("fb_token", newToken, { expires: 1 }); // 1 day
    setToken(newToken);
  };

  const clearToken = () => {
    Cookies.remove("fb_token");
    Cookies.remove("fb_insights"); // optional: clear cached insights
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, updateToken, clearToken }}>
      {children}
    </AuthContext.Provider>
  );
};
