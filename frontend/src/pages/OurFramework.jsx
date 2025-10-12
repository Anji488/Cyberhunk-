import React from "react";
import { Cpu, Shield, Eye, MessageCircle, Zap } from "lucide-react";

const OurFramework = () => {
  const features = [
    {
      title: "Sentiment Analysis",
      desc: "Analyzes the emotional tone of user-generated content, including text and emojis, to provide insights into digital communication patterns.",
      icon: <MessageCircle className="h-12 w-12 text-indigo-500" />,
    },
    {
      title: "Privacy Detection",
      desc: "Identifies unintentional exposure of personal information, keeping users aware of potential privacy risks in their posts.",
      icon: <Eye className="h-12 w-12 text-green-500" />,
    },
    {
      title: "Toxicity Detection",
      desc: "Detects harmful language and cyberbullying behavior, ensuring safer online engagement.",
      icon: <Zap className="h-12 w-12 text-red-500" />,
    },
    {
      title: "Misinformation Recognition",
      desc: "Analyzes shared content to spot misleading or false information, promoting responsible content sharing.",
      icon: <Shield className="h-12 w-12 text-yellow-500" />,
    },
    {
      title: "Secure Data Acquisition",
      desc: "Uses Meta Graph API with OAuth2 authentication ensuring safe, authorized access to user-generated content.",
      icon: <Cpu className="h-12 w-12 text-pink-500" />,
    },
  ];

  return (
    <section className="bg-gradient-to-br from-purple-50 to-indigo-50 py-16 px-6">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-4xl font-extrabold text-gray-800 mb-4 drop-shadow-md">
          CYBERHUNK SafeGuard Framework
        </h2>
        <p className="text-lg text-gray-700 mb-12 max-w-3xl mx-auto">
          A comprehensive AI-driven system for analyzing responsible social media usage. Our framework evaluates multi-dimensional behavioral patterns including sentiment, privacy, toxicity, and misinformation to provide actionable insights for digital citizenship.
        </p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((f, i) => (
            <div
              key={i}
              className="bg-white rounded-3xl shadow-lg p-6 hover:shadow-xl transition duration-300 transform hover:scale-105"
            >
              <div className="mb-4 flex justify-center">{f.icon}</div>
              <h3 className="text-2xl font-semibold text-gray-800 mb-2">{f.title}</h3>
              <p className="text-gray-600">{f.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-12">
          <p className="text-gray-700 text-lg max-w-3xl mx-auto leading-relaxed">
            The SafeGuard Framework leverages advanced AI techniques, transformer-based models, and ethical data handling principles. It ensures secure data acquisition, multi-dimensional analysis, and intuitive insight presentation to empower users to improve their digital responsibility.
          </p>
        </div>
      </div>
    </section>
  );
};

export default OurFramework;
