import React from "react";
import {
  ShieldCheckIcon,
  ChatBubbleLeftRightIcon,
  EyeIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

const features = [
  {
    name: "Sentiment Analysis",
    description:
      "Detects emotions and tone in user content, helping to understand the mood and intent of social interactions.",
    icon: ChatBubbleLeftRightIcon,
  },
  {
    name: "Privacy Protection",
    description:
      "Ensures sensitive or personal data is protected through robust privacy measures and compliance.",
    icon: ShieldCheckIcon,
  },
  {
    name: "Toxicity Detection",
    description:
      "Identifies and flags harmful or offensive language to promote safer online communication.",
    icon: ExclamationTriangleIcon,
  },
  {
    name: "Misinformation Analysis",
    description:
      "Analyzes content to detect misleading or false information, supporting fact-based digital literacy.",
    icon: EyeIcon,
  },
];

export default function Features() {
  return (
    <div className="bg-gray-50 min-h-screen py-20 px-6">
      <div className="max-w-6xl mx-auto text-center">
        <h2 className="text-indigo-600 font-semibold uppercase tracking-wide">
          Core Features
        </h2>
        <p className="mt-2 text-4xl font-extrabold text-gray-900 sm:text-5xl">
          What Makes SafeGuard Unique
        </p>
        <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
          Our framework combines AI-driven tools with user-friendly insights to
          create a safer, more responsible digital environment.
        </p>
      </div>

      <div className="mt-16 grid gap-10 sm:grid-cols-2 lg:grid-cols-4 max-w-6xl mx-auto">
        {features.map((feature) => (
          <div
            key={feature.name}
            className="bg-white rounded-xl shadow-md p-6 text-center hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-center h-16 w-16 mx-auto rounded-full bg-indigo-100 text-indigo-600 mb-6">
              <feature.icon className="h-8 w-8" aria-hidden="true" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              {feature.name}
            </h3>
            <p className="mt-3 text-gray-600 text-sm leading-relaxed">
              {feature.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
