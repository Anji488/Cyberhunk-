import React from "react";
import SectionTitle from "./SectionTitle";
import { Target, Cpu, Star } from "lucide-react";

const Mission = () => {
  return (
    <section className="relative py-20 px-6 bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50 overflow-hidden">

      <div className="absolute -top-16 -left-16 w-48 h-48 bg-pink-300 rounded-full opacity-30 animate-bounce-slow blur-3xl"></div>
      <div className="absolute top-32 -right-24 w-64 h-64 bg-purple-300 rounded-full opacity-20 animate-bounce-slow blur-3xl"></div>
      <div className="absolute bottom-0 left-1/3 w-40 h-40 bg-indigo-300 rounded-full opacity-25 animate-bounce-slow blur-3xl"></div>

      <div className="absolute top-10 left-1/4 w-24 h-16 bg-white/80 rounded-2xl shadow-lg rotate-6 animate-float-slow blur-md"></div>
      <div className="absolute top-48 right-1/4 w-32 h-20 bg-white/70 rounded-2xl shadow-lg -rotate-6 animate-float-slow blur-md"></div>
      <div className="absolute bottom-20 left-1/2 w-28 h-16 bg-white/75 rounded-2xl shadow-lg rotate-3 animate-float-slow blur-md"></div>

      <div className="relative max-w-5xl mx-auto text-center z-10">
        <SectionTitle
          title="Our Mission"
          subtitle="Promoting digital citizenship through AI-driven insights"
        />

        <p className="text-lg md:text-xl text-gray-800 dark:text-gray-700 leading-relaxed mt-6 max-w-3xl mx-auto">
          Our mission is to empower individuals with personalized insights into their social media
          behavior, fostering responsible online engagement while addressing challenges like
          cyberbullying, misinformation, and privacy risks.
        </p>

        <div className="mt-10 flex justify-center space-x-6">
          <div className="w-16 h-16 bg-pink-400 rounded-full flex items-center justify-center shadow-xl text-white animate-bounce">
            <Target className="w-8 h-8" />
          </div>
          <div className="w-16 h-16 bg-purple-400 rounded-full flex items-center justify-center shadow-xl text-white animate-bounce delay-150">
            <Cpu className="w-8 h-8" />
          </div>
          <div className="w-16 h-16 bg-indigo-400 rounded-full flex items-center justify-center shadow-xl text-white animate-bounce delay-300">
            <Star className="w-8 h-8" />
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes bounce-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .animate-bounce-slow {
          animation: bounce-slow 6s infinite;
        }
        .animate-bounce {
          animation: bounce-slow 2s infinite;
        }
        .delay-150 { animation-delay: 0.15s; }
        .delay-300 { animation-delay: 0.3s; }

        @keyframes float-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }
        .animate-float-slow {
          animation: float-slow 8s infinite ease-in-out;
        }
      `}</style>
    </section>
  );
};

export default Mission;
