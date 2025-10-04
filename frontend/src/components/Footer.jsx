import { FaGithub, FaLinkedin } from "react-icons/fa";
import { NavLink } from "react-router-dom";
import Cookies from "js-cookie";

export default function Footer() {
  const token = Cookies.get("fb_token"); 

  return (
    <footer className="bg-indigo-900 text-white py-16 relative">
      <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-12">

        <div>
          <h4 className="font-semibold text-lg mb-4 border-b border-white/30 pb-2">Quick Links</h4>
          <ul className="space-y-2">
            <li>
              <NavLink to="/" className="hover:text-pink-400 transition-colors">Home</NavLink>
            </li>
            <li>
              <NavLink to="/about" className="hover:text-pink-400 transition-colors">About</NavLink>
            </li>
            <li>
              <NavLink to="/features" className="hover:text-pink-400 transition-colors">Features</NavLink>
            </li>
          </ul>
        </div>

        {token && (
          <div>
            <h4 className="font-semibold text-lg mb-4 border-b border-white/30 pb-2">Take Test Links</h4>
            <ul className="space-y-2">
              <li>
                <NavLink to="/dashboard" className="hover:text-pink-400 transition-colors">Dashboard</NavLink>
              </li>
              <li>
                <NavLink to="/charts" className="hover:text-pink-400 transition-colors">Charts</NavLink>
              </li>
              <li>
                <NavLink to="/posts" className="hover:text-pink-400 transition-colors">Posts</NavLink>
              </li>
            </ul>
          </div>
        )}

        <div>
          <h4 className="font-semibold text-lg mb-4 border-b border-white/30 pb-2">Resources</h4>
          <ul className="space-y-2">
            {!token && (
              <li>
                <NavLink to="/login" className="hover:text-purple-400 transition-colors">Login / Take Test</NavLink>
              </li>
            )}
            <li>
              <NavLink to="/our-framework" className="hover:text-purple-400 transition-colors">Our Framework</NavLink>
            </li>
          </ul>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 mt-12 border-t border-white/20 pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="text-sm text-white/80">&copy; 2025 Cyber Hunk. All rights reserved.</p>
        <div className="flex gap-4 text-sm">
          <NavLink to="/privacy-policy" className="hover:text-purple-400 transition-colors">Privacy Policy</NavLink>
          <NavLink to="/terms" className="hover:text-purple-400 transition-colors">Terms of Service</NavLink>
        </div>
        <div className="flex gap-4 text-2xl mt-4 md:mt-0">
          <a href="https://github.com/Anji488" className="hover:text-pink-400 transition-colors"><FaGithub /></a>
          <a href="https://www.linkedin.com/in/anjani-wijayaratne-31964921" className="hover:text-blue-600 transition-colors"><FaLinkedin /></a>
        </div>
      </div>

      <div className="absolute -top-10 -left-10 w-40 h-40 bg-pink-400 rounded-full opacity-20 animate-pulse-slow blur-3xl"></div>
      <div className="absolute top-20 right-10 w-60 h-60 bg-purple-400 rounded-full opacity-15 animate-pulse-slow blur-3xl"></div>
      <div className="absolute bottom-0 left-1/3 w-56 h-56 bg-indigo-500 rounded-full opacity-15 animate-pulse-slow blur-3xl"></div>

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 0.5; }
        }
        .animate-pulse-slow { animation: pulse 6s infinite; }
      `}</style>
    </footer>
  );
}
