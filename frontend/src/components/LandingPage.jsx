import Navbar from './Navbar';
import Hero from './Hero';
import Features from './Features';
import HowItWorks from './HowItWorks';
import Pricing from './Pricing';
import CTA from './CTA';
import Footer from './Footer';
import SplineBot from './SplineBot';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <Navbar />
      <Hero />
      <SplineBot />
      <Features />
      <HowItWorks />
      <CTA />
      <Footer />
    </div>
  );
}
