import React from "react";
import { useNavigate } from "react-router-dom";

const HeroBanner = ({ title, subtitle, image }) => {
  const navigate = useNavigate();
  return (
    <section
      className="relative w-full h-[92vh] flex items-center justify-end text-right"
      style={{
        backgroundImage: `url(${image})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >

      <div className="relative z-10 text-white px-6 max-w-3xl">
        <h1 className="text-5xl font-extrabold mb-4 drop-shadow-lg">{title}</h1>
        <p className="text-lg md:text-xl leading-relaxed drop-shadow-md">{subtitle}</p>

        <div className="flex justify-end mt-6">
          <button
            onClick={() => navigate("/login")}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-purple-600 hover:to-indigo-500 text-white font-semibold text-xl md:text-2xl px-14 py-5 rounded-full shadow-2xl flex items-center space-x-4 transition-all duration-300 transform hover:scale-105 hover:shadow-indigo-500/50"
          >
            <span>Take a Test</span>
            <span className="text-3xl">→</span>
          </button>
        </div>
      </div>

    </section>
  );
};

export default HeroBanner;
