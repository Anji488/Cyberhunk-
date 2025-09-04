// File: src/components/Layout.jsx
import React, { useState, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { FaChartPie, FaUserCircle, FaListUl, FaBars, FaSignOutAlt } from "react-icons/fa";
import Cookies from "js-cookie";

export default function Layout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const token = Cookies.get("fb_token");

  // 🔹 If no token, redirect to login
  useEffect(() => {
    if (!token) {
      navigate("/login");
    }
  }, [token, navigate]);

  const handleToggle = () => setCollapsed(!collapsed);

  const handleLogout = () => {
    Cookies.remove("fb_token");
    Cookies.remove("fb_insights");
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen max-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-gray-100 overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`bg-gray-900 shadow-lg flex flex-col justify-between border-r border-gray-700 transition-all duration-300 ${
          collapsed ? "w-20" : "w-64"
        }`}
      >
        <div>
          <div className="flex items-center justify-between p-6">
            {!collapsed && (
              <h1 className="text-2xl font-bold text-indigo-400">Cyber Hunk</h1>
            )}
            <button
              onClick={handleToggle}
              className="text-indigo-400 hover:text-indigo-200 focus:outline-none"
            >
              <FaBars />
            </button>
          </div>

          <nav className="flex flex-col space-y-4 mt-4 px-2">
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `flex items-center gap-3 p-3 rounded-lg transition ${
                  isActive ? "bg-indigo-500 text-white" : "hover:bg-gray-700"
                }`
              }
            >
              <FaUserCircle className="flex-shrink-0" />
              {!collapsed && "Dashboard"}
            </NavLink>
            <NavLink
              to="/charts"
              className={({ isActive }) =>
                `flex items-center gap-3 p-3 rounded-lg transition ${
                  isActive ? "bg-indigo-500 text-white" : "hover:bg-gray-700"
                }`
              }
            >
              <FaChartPie className="flex-shrink-0" />
              {!collapsed && "Distribution Charts"}
            </NavLink>
            <NavLink
              to="/posts"
              className={({ isActive }) =>
                `flex items-center gap-3 p-3 rounded-lg transition ${
                  isActive ? "bg-indigo-500 text-white" : "hover:bg-gray-700"
                }`
              }
            >
              <FaListUl className="flex-shrink-0" />
              {!collapsed && "Post-by-Post"}
            </NavLink>
          </nav>
        </div>

        <div className="px-0 py-4">
          {token && (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-red-500 hover:text-red-400 w-full p-4 rounded-lg transition"
            >
              <FaSignOutAlt /> {!collapsed && "Logout"}
            </button>
          )}
          {!collapsed && (
            <p className="text-xs text-gray-400 pl-4 mt-2">© 2025 Cyber Hunk</p>
          )}
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">{children}</main>
    </div>
  );
}
