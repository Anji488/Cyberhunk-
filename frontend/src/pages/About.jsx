import React from "react";
import HeroBanner from "../components/about/HeroBanner";
import Features from "../components/about/Features";
import Mission from "../components/about/Mission";

const About = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <HeroBanner
        title="About SafeGuard Framework"
        subtitle="An AI-driven platform promoting responsible social media through sentiment, privacy, toxicity, and misinformation analysis."
        image="/images/about.png"
      />
      <Features />
      <Mission />
    </div>
  );
};

export default About;
