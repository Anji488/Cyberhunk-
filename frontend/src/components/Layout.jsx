import React, { useState, useEffect, useRef } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { FaSignOutAlt, FaUserCircle } from "react-icons/fa";
import Cookies from "js-cookie";
import Footer from "./Footer";

export default function Layout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const navigate = useNavigate();
  const token = Cookies.get("fb_token");

  const profileRef = useRef();

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    Cookies.remove("fb_token");
    Cookies.remove("fb_insights");
    navigate("/login");
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
    
      <nav className="w-full backdrop-blur-lg bg-white/70 shadow-md fixed top-0 left-0 z-50 flex items-center justify-between px-6 py-3">
    
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-indigo-600">Cyber Hunk</h1>
        </div>

        <div className={`flex gap-6 items-center ${menuOpen ? "flex" : "hidden md:flex"}`}>

          <NavLink
            to="/"
            className={({ isActive }) =>
              `text-gray-700 hover:text-indigo-500 font-semibold transition ${isActive ? "text-indigo-600" : ""}`
            }
          >
            Home
          </NavLink>
          <NavLink
            to="/about"
            className={({ isActive }) =>
              `text-gray-700 hover:text-indigo-500 font-semibold transition ${isActive ? "text-indigo-600" : ""}`
            }
          >
            About
          </NavLink>
          <NavLink
            to="/features"
            className={({ isActive }) =>
              `text-gray-700 hover:text-indigo-500 font-semibold transition ${isActive ? "text-indigo-600" : ""}`
            }
          >
            Features
          </NavLink>

          {token ? (
            <>
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `text-gray-700 hover:text-indigo-500 font-semibold transition ${isActive ? "text-indigo-600" : ""}`
                }
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/charts"
                className={({ isActive }) =>
                  `text-gray-700 hover:text-indigo-500 font-semibold transition ${isActive ? "text-indigo-600" : ""}`
                }
              >
                Charts
              </NavLink>
              <NavLink
                to="/posts"
                className={({ isActive }) =>
                  `text-gray-700 hover:text-indigo-500 font-semibold transition ${isActive ? "text-indigo-600" : ""}`
                }
              >
                Posts
              </NavLink>

              <div className="relative" ref={profileRef}>
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-1 text-gray-700 hover:text-indigo-500 transition text-lg"
                >
                  <FaUserCircle className="h-6 w-6" />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 shadow-lg rounded-md py-2 z-50">
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-red-500 hover:bg-gray-100 flex items-center gap-2"
                    >
                      <FaSignOutAlt /> Logout
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <NavLink
              to="/login"
              className="text-gray-700 hover:text-indigo-500 font-semibold transition"
            >
              Login
            </NavLink>
          )}
        </div>
      </nav>

      <main className="pt-14 flex-1 overflow-y-auto">{children}</main>

      <Footer />
    </div>
  );
}
