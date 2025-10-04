import HeroBanner from "../components/home/HeroBanner";
import IntroductionBlock from "../components/home/IntroductionBlock";
import CoreFeatures from "../components/home/CoreFeatures";
import Methodology from "../components/home/Methodology";
import FutureRoadmap from "../components/home/FutureRoadmap";
import ImpactSection from "../components/home/ImpactSection";

export default function HomePage() {
  return (
    <div>
      <HeroBanner />
      <IntroductionBlock />
      <CoreFeatures />
      <FutureRoadmap />
      <Methodology />
      <ImpactSection />
    </div>
  );
}
