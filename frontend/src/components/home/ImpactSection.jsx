import { Sun, BookOpen, Globe } from "lucide-react";
import { motion } from "framer-motion";

export default function ImpactSection() {
  const impacts = [
    { title: "Individuals", desc: "Better self-awareness of digital behavior.", icon: <Sun className="w-6 h-6 text-white" /> },
    { title: "Educators", desc: "Tool for teaching digital citizenship.", icon: <BookOpen className="w-6 h-6 text-white" /> },
    { title: "Society", desc: "Reduce cyberbullying, misinformation, and promote digital wellness.", icon: <Globe className="w-6 h-6 text-white" /> },
  ];

  return (
    <section className="py-24 bg-white relative overflow-hidden">
      <div className="absolute -top-20 -left-20 w-72 h-72 bg-pink-100 rounded-full opacity-30 animate-pulse-slow blur-3xl"></div>
      <div className="absolute top-40 -right-32 w-96 h-96 bg-purple-100 rounded-full opacity-20 animate-pulse-slow blur-3xl"></div>
      <div className="absolute bottom-0 left-1/3 w-64 h-64 bg-indigo-100 rounded-full opacity-25 animate-pulse-slow blur-3xl"></div>

      <div className="max-w-6xl mx-auto px-4 text-center mb-12 relative z-10">
        <h2 className="text-4xl font-extrabold text-indigo-900 drop-shadow-sm">Impact</h2>
        <p className="text-gray-700 mt-4">How CyberHunk adds value.</p>
      </div>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
        {impacts.map((impact, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.7, delay: i * 0.2 }}
            className="relative p-6 rounded-3xl shadow-xl bg-white/70 backdrop-blur-lg border border-gray-200 hover:scale-105 hover:shadow-2xl transition-transform cursor-pointer"
          >
            <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 w-12 h-12 rounded-full flex items-center justify-center bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 shadow-lg animate-gradient-neon">
              {impact.icon}
            </div>

            <h3 className="text-2xl font-bold text-indigo-900 mt-6 mb-2 text-center">{impact.title}</h3>
            <p className="text-gray-700 text-center">{impact.desc}</p>
          </motion.div>
        ))}
      </div>

      <style jsx>{`
        @keyframes gradient-neon {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .animate-gradient-neon {
          background-size: 200% 200%;
          animation: gradient-neon 3s ease infinite;
        }
      `}</style>
    </section>
  );
}
