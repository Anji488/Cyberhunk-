import React from "react";
import SectionTitle from "./SectionTitle";
import { ShieldCheckIcon, ChatBubbleLeftRightIcon, EyeIcon, ExclamationTriangleIcon } from "@heroicons/react/24/outline";

const features = [
  {
    title: "Sentiment Analysis",
    desc: "Understand emotional tones in text & emoji-based content.",
    icon: ChatBubbleLeftRightIcon,
    color: "bg-pink-400",
  },
  {
    title: "Privacy Detection",
    desc: "Identify potential privacy disclosures in posts.",
    icon: EyeIcon,
    color: "bg-purple-400",
  },
  {
    title: "Toxicity Detection",
    desc: "Detect harmful language and cyberbullying patterns.",
    icon: ExclamationTriangleIcon,
    color: "bg-yellow-400",
  },
  {
    title: "Misinformation Recognition",
    desc: "Spot misleading or fake content with AI-driven insights.",
    icon: ShieldCheckIcon,
    color: "bg-indigo-400",
  },
];

const Features = () => {
  return (
    <section className="py-20 px-6 bg-gradient-to-b from-pink-50 via-purple-50 to-indigo-50">
      <SectionTitle title="Core Features" subtitle="Multi-dimensional AI-powered analysis" />
      
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto mt-12">
        {features.map((f, i) => (
          <div
            key={i}
            className="relative p-6 rounded-3xl shadow-lg hover:shadow-2xl transition-transform duration-300 transform hover:scale-105 bg-white/80 backdrop-blur-md border border-gray-200"
          >
            <div className={`w-16 h-16 flex items-center justify-center rounded-full mb-4 ${f.color} shadow-xl`}>
              <f.icon className="h-8 w-8 text-white" />
            </div>

            <h3 className="text-xl font-bold text-indigo-900 mb-2">{f.title}</h3>
            <p className="text-gray-700">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Features;
