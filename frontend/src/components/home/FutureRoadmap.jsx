import { motion } from "framer-motion";
import { Brain, Activity, BarChart3, Database } from "lucide-react";
import "./home.css"; 

export default function FutureRoadmap() {
  const roadmap = [
    {
      title: "AI Optimization",
      desc: "Advanced machine learning models will reduce toxicity, misinformation, and improve contextual accuracy across platforms.",
      icon: Brain,
    },
    {
      title: "Real-Time Feedback",
      desc: "Live monitoring with instant feedback loops to track behaviors and deliver actionable insights instantly.",
      icon: Activity,
    },
    {
      title: "Interactive Dashboards",
      desc: "User-friendly dashboards with deep analytics, usage tracking, and custom reporting for better engagement.",
      icon: BarChart3,
    },
    {
      title: "Secure Integrations",
      desc: "Seamless integration with encrypted databases to ensure privacy, scalability, and long-term secure insights.",
      icon: Database,
    },
  ];

  const containerVariants = {
    hidden: {},
    show: {
      transition: { staggerChildren: 0.35 },
    },
  };

  const itemVariants = (isLeft) => ({
    hidden: { opacity: 0, x: isLeft ? -120 : 120, scale: 0.9 },
    show: {
      opacity: 1,
      x: 0,
      scale: 1,
      transition: { duration: 0.7, ease: "easeOut" },
    },
  });

  return (
    <section className="py-24 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-6xl mx-auto px-4 text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-extrabold text-indigo-900 drop-shadow-sm">
          Future Roadmap
        </h2>
        <p className="text-gray-600 mt-4 text-lg max-w-2xl mx-auto">
          Our vision for the future — powerful AI, real-time insights, modern dashboards, and secure data integrations.
        </p>
      </div>

      <div className="max-w-5xl mx-auto relative">
        <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-gradient-to-b from-indigo-500 via-purple-500 to-pink-500 rounded-full" />

        <motion.ul
          variants={containerVariants}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, amount: 0.2 }}
        >
          {roadmap.map((item, i) => {
            const Icon = item.icon;
            return (
              <motion.li
                key={i}
                variants={itemVariants(i % 2 === 0)}
                className={`relative flex md:items-center ${i % 2 === 0 ? "md:justify-start" : "md:justify-end"} justify-center`}
              >
                <div className="absolute left-1/2 transform -translate-x-1/2 w-14 h-14 flex items-center justify-center rounded-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg animate-pulse-slow">
                  <Icon size={24} />
                </div>

                <div className={`w-11/12 md:w-5/12 ${i % 2 === 0 ? "md:pr-12 md:text-right text-center" : "md:pl-12 md:text-left text-center"}`}>
                  <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition duration-300 border border-gray-100">
                    <h3 className="text-xl font-bold text-indigo-900 mb-2">{item.title}</h3>
                    <p className="text-gray-700 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              </motion.li>
            );
          })}
        </motion.ul>
      </div>
    </section>
  );
}
