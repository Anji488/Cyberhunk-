import { FaSmile, FaLock, FaBan, FaNewspaper, FaChartLine } from "react-icons/fa";
import { motion } from "framer-motion";

const features = [
  {
    title: "Sentiment Analysis",
    icon: <FaSmile size={28} />,
    description: "Understand emotional tone of posts (text + emojis).",
    color: "bg-green-100 text-green-600",
  },
  {
    title: "Privacy Disclosure Detection",
    icon: <FaLock size={28} />,
    description: "Identifies accidental sharing of sensitive data (like email, location).",
    color: "bg-indigo-100 text-indigo-600",
  },
  {
    title: "Toxicity & Cyberbullying Detection",
    icon: <FaBan size={28} />,
    description: "Detects harmful or harassing language.",
    color: "bg-red-100 text-red-600",
  },
  {
    title: "Misinformation Recognition",
    icon: <FaNewspaper size={28} />,
    description: "Flags potentially misleading/fake content.",
    color: "bg-yellow-100 text-yellow-600",
  },
  {
    title: "Analytical Insights Dashboard",
    icon: <FaChartLine size={28} />,
    description: "Provides personalized digital responsibility score + recommendations.",
    color: "bg-purple-100 text-purple-600",
  },
];

export default function CoreFeatures() {
  return (
    <section className="py-24 bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 text-center mb-12">
        <h2 className="text-4xl font-extrabold text-indigo-900">Core Features</h2>
        <p className="text-gray-700 mt-4 text-lg">Explore CyberHunk's key functionalities.</p>
      </div>

      <div className="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {features.map((feature, i) => (
          <motion.div
            key={i}
            whileHover={{ scale: 1.05, y: -5 }}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.5, delay: i * 0.15 }}
            className="bg-white p-6 rounded-2xl shadow-lg flex flex-col items-start gap-4 cursor-pointer border border-gray-100 hover:shadow-xl hover:border-indigo-300 transition"
          >
            <div className={`w-12 h-12 flex items-center justify-center rounded-full ${feature.color} text-xl`}>
              {feature.icon}
            </div>

            <h3 className="text-xl font-semibold text-indigo-900">{feature.title}</h3>
            <p className="text-gray-700">{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
