// File: src/context/AuthContext.jsx
import React, { createContext, useState, useEffect } from "react";
import Cookies from "js-cookie";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const savedToken = Cookies.get("fb_token");
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  const updateToken = (newToken) => {
    Cookies.set("fb_token", newToken, {
      expires: 7,
      sameSite: "Lax",
      secure: true,
    });

    Cookies.remove("fb_insights"); // reset cached insights
    setToken(newToken);
  };

  const logout = () => {
    Cookies.remove("fb_token");
    Cookies.remove("fb_insights");
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, updateToken, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
