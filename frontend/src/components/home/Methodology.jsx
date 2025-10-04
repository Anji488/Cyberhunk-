import { motion, useAnimation } from "framer-motion";
import { useRef, useEffect } from "react";
import { useInView } from "framer-motion";
import { Lock, Settings, Cpu, BarChart2 } from "lucide-react";

export default function Methodology() {
  const steps = [
    {
      title: "Secure Data Acquisition",
      desc: "via Meta’s Graph API + OAuth 2.0",
      icon: <Lock className="w-6 h-6 text-white" />,
    },
    {
      title: "Data Processing",
      desc: "Cleaning, emoji handling, multilingual support",
      icon: <Settings className="w-6 h-6 text-white" />,
    },
    {
      title: "AI Engine",
      desc: "BERT, RoBERTa, NLP models for text & emoji",
      icon: <Cpu className="w-6 h-6 text-white" />,
    },
    {
      title: "User Presentation",
      desc: "Interactive dashboards, charts, recommendations",
      icon: <BarChart2 className="w-6 h-6 text-white" />,
    },
  ];

  return (
    <section className="py-28 relative overflow-hidden bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50">
 
      <div className="absolute -top-20 -left-20 w-72 h-72 bg-pink-300 rounded-full opacity-30 animate-pulse-slow blur-3xl"></div>
      <div className="absolute top-40 -right-32 w-96 h-96 bg-purple-300 rounded-full opacity-20 animate-pulse-slow blur-3xl"></div>
      <div className="absolute bottom-0 left-1/3 w-64 h-64 bg-indigo-300 rounded-full opacity-25 animate-pulse-slow blur-3xl"></div>

      <div className="relative max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center gap-16 z-10">

        <div className="flex-1 space-y-8">
          <h2 className="text-4xl md:text-5xl font-extrabold text-indigo-900 drop-shadow-sm">
            Methodology
          </h2>
          <p className="text-gray-700 text-lg md:text-xl max-w-lg">
            How CyberHunk works under the hood — innovative, AI-powered, and proactive.
          </p>

          <div className="relative grid md:grid-cols-2 gap-6">
            {steps.map((step, i) => {
              const ref = useRef(null);
              const inView = useInView(ref, { once: true, amount: 0.5 });
              const controls = useAnimation();

              useEffect(() => {
                if (inView) {
                  controls.start({ width: "100%" });
                }
              }, [inView, controls]);

              return (
                <motion.div
                  ref={ref}
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.3 }}
                  transition={{ duration: 0.7, delay: i * 0.2 }}
                  className="relative p-6 rounded-3xl shadow-xl bg-white/70 backdrop-blur-lg cursor-pointer hover:scale-105 hover:shadow-2xl transition-transform border border-gray-200"
                >
                  <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 w-12 h-12 rounded-full flex items-center justify-center bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 shadow-lg animate-gradient-neon">
                    {step.icon}
                  </div>

                  <h3 className="text-2xl font-bold text-indigo-900 mt-6 mb-2 text-center md:text-left">
                    {step.title}
                  </h3>
                  <p className="text-gray-700 text-center md:text-left">{step.desc}</p>

                </motion.div>
              );
            })}
          </div>
        </div>

        <motion.div
          className="flex-1"
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.8 }}
        >
          <img
            src="/images/method.png" 
            alt="Methodology Cartoon"
            className="w-full max-w-md mx-auto rounded-2xl shadow-2xl hover:scale-105 transition-transform"
          />
        </motion.div>
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
