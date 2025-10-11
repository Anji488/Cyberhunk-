import { useNavigate } from "react-router-dom";

export default function HomeHero() {
  const navigate = useNavigate();

  return (
    <section
      className="relative flex justify-center items-start text-center pt-24 md:pt-6" 
      style={{
        height: "100vh",
        backgroundImage: "url('/images/homeHero.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        imageRendering: "auto",
      }}
    >
      <div className="relative z-10 max-w-5xl mx-auto px-4 flex flex-col items-center">
        <h1 className="text-4xl md:text-6xl font-extrabold mb-6 text-indigo-900">
          CyberHunk: AI-Powered SafeGuard Framework
        </h1>
        <p className="text-lg md:text-2xl mb-8 text-gray-700">
          Promoting responsible social media use through AI-driven insights
        </p>
        <button
          onClick={() => navigate("/login")}
          className="bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-purple-600 hover:to-indigo-500 text-white font-semibold text-xl md:text-2xl px-14 py-5 rounded-full shadow-2xl flex items-center space-x-4 transition-all duration-300 transform hover:scale-105 hover:shadow-indigo-500/50"
        >
          <span>Take a Test</span>
          <span className="text-3xl">→</span>
        </button>
      </div>
    </section>
  );
}
