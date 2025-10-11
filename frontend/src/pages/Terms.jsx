import React from "react";
import HeroBanner from "@/components/partials/HeroBanner";

export default function Terms() {
  return (
    <div className="min-h-screen flex flex-col">
      <HeroBanner
        title="Terms & Conditions"
        subtitle="By using our platform, you agree to follow these terms and conditions."
        image="https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1600&q=80"
      />

      <div className="bg-gray-50 py-20 px-6 flex-1">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold mt-8 mb-3">1. Use of Service</h2>
          <p className="text-gray-600 mb-4">
            You agree to use our services responsibly and not engage in harmful,
            abusive, or illegal activities.
          </p>

          <h2 className="text-2xl font-semibold mt-8 mb-3">2. Intellectual Property</h2>
          <p className="text-gray-600 mb-4">
            All content, branding, and intellectual property belong to SafeGuard
            Framework unless otherwise stated.
          </p>

          <h2 className="text-2xl font-semibold mt-8 mb-3">3. Limitation of Liability</h2>
          <p className="text-gray-600 mb-4">
            SafeGuard Framework is not liable for any damages resulting from
            misuse of the platform or reliance on provided insights.
          </p>

          <h2 className="text-2xl font-semibold mt-8 mb-3">4. Changes to Terms</h2>
          <p className="text-gray-600 mb-4">
            We reserve the right to update or modify these terms at any time. You
            are responsible for reviewing them periodically.
          </p>

          <h2 className="text-2xl font-semibold mt-8 mb-3">5. Contact Us</h2>
          <p className="text-gray-600">
            If you have questions about these Terms, please contact us via{" "}
            <a href="/contact" className="text-indigo-600 hover:underline">
              our support page
            </a>.
          </p>
        </div>
      </div>
    </div>
  );
}
