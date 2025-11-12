// File: src/pages/Login.jsx
import React from "react";
import { FaFacebookF } from "react-icons/fa";
import { Sun, BookOpen, Globe } from "lucide-react";
import { motion } from "framer-motion";

export default function Login() {
  const BACKEND_URL = "https://spurtive-subtilely-earl.ngrok-free.dev";
  return (
    <div className="min-h-screen relative bg-white font-sans overflow-hidden flex flex-col items-center justify-start py-20 px-6 md:px-20">

      {/* Background cartoon shapes */}
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-pink-200 rounded-full opacity-30 animate-pulse-slow blur-3xl"></div>
      <div className="absolute top-40 -right-40 w-96 h-96 bg-purple-200 rounded-full opacity-20 animate-pulse-slow blur-3xl"></div>
      <div className="absolute bottom-0 left-1/3 w-72 h-72 bg-indigo-200 rounded-full opacity-25 animate-pulse-slow blur-3xl"></div>

      {/* Floating neon bubbles */}
      <div className="absolute top-10 left-1/4 w-12 h-12 rounded-full bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 opacity-70 animate-bounce-slow"></div>
      <div className="absolute top-1/2 right-1/3 w-16 h-16 rounded-full bg-gradient-to-r from-purple-400 via-indigo-400 to-pink-400 opacity-60 animate-bounce-slow"></div>
      <div className="absolute bottom-20 left-2/3 w-20 h-20 rounded-full bg-gradient-to-r from-indigo-400 via-pink-400 to-purple-400 opacity-50 animate-bounce-slow"></div>

      {/* Page Heading */}
      <motion.h1
        className="text-indigo-900 text-4xl md:text-5xl font-extrabold text-center mb-6 drop-shadow-lg"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        CyberHunk: Digital Responsibility Made Fun
      </motion.h1>

      {/* Project Description */}
      <motion.div
        className="max-w-3xl text-center mb-12 space-y-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 0.3 }}
      >
        <p className="text-gray-700 text-lg md:text-xl">
          CyberHunk is an interactive tool designed to help individuals, educators, and society at large
          understand and improve their digital behavior. By analyzing social media interactions, emoji usage,
          and communication patterns, it gives personalized insights that promote mindful digital practices.
        </p>
        <p className="text-gray-700 text-lg md:text-xl">
          Educators can use CyberHunk to teach digital citizenship, individuals gain better self-awareness,
          and society benefits from reduced misinformation, cyberbullying, and a healthier online culture.
        </p>
        <p className="text-gray-700 text-lg md:text-xl">
          The project leverages cutting-edge AI models, natural language processing, and intuitive visualizations
          to make understanding digital behavior simple, fun, and engaging.
        </p>
      </motion.div>

      {/* Floating icons around the text */}
      <Sun className="absolute top-32 left-10 w-12 h-12 text-pink-400 animate-spin-slow opacity-80" />
      <BookOpen className="absolute top-1/2 right-10 w-16 h-16 text-purple-400 animate-spin-slow opacity-70" />
      <Globe className="absolute bottom-32 left-1/3 w-20 h-20 text-indigo-400 animate-spin-slow opacity-60" />

      {/* Facebook Login Button */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, delay: 0.6 }}
      >
        <a href={`${BACKEND_URL}/auth/facebook`}>
          <button className="group relative bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-xl transition-all duration-300 shadow-lg text-lg flex items-center justify-center overflow-hidden">
            <span className="absolute left-0 w-12 h-12 bg-white/10 rounded-full transform scale-0 group-hover:scale-150 transition-transform duration-700 ease-out" />
            <FaFacebookF className="mr-3 text-xl z-10" />
            <span className="z-10">Take the Test with Facebook</span>
          </button>
        </a>
      </motion.div>

      {/* Animations */}
      <style>{`
        @keyframes gradient-neon {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.6; }
        }
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-20px); }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .animate-gradient-neon {
          background-size: 200% 200%;
          animation: gradient-neon 3s ease infinite;
        }
        .animate-pulse-slow {
          animation: pulse 6s infinite;
        }
        .animate-bounce-slow {
          animation: bounce 6s infinite;
        }
        .animate-spin-slow {
          animation: spin 20s linear infinite;
        }
      `}</style>
    </div>
  );
}
