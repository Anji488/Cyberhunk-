import React from "react";
import HeroBanner from "@/components/partials/HeroBanner";

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen flex flex-col">
      <HeroBanner
        title="Privacy Policy"
        subtitle="Your privacy is important to us. Learn how we collect, use, and safeguard your data."
        image="https://t3.ftcdn.net/jpg/15/33/36/62/240_F_1533366277_CxbeG8Znuf1HI2GYEQ1VCwue67dgjQAm.jpg"
      />

      <div className="bg-gray-50 py-20 px-6 flex-1">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold mt-8 mb-3">1. Information We Collect</h2>
          <p className="text-gray-600 mb-4">
            We may collect personal information such as your name, email address,
            and usage data when you interact with our platform.
          </p>

          <h2 className="text-2xl font-semibold mt-8 mb-3">2. How We Use Information</h2>
          <p className="text-gray-600 mb-4">
            Information is used to improve our services, enhance user experience,
            and ensure platform security.
          </p>

          <h2 className="text-2xl font-semibold mt-8 mb-3">3. Data Security</h2>
          <p className="text-gray-600 mb-4">
            We implement industry-standard measures to protect your data against
            unauthorized access, disclosure, or misuse.
          </p>

          <h2 className="text-2xl font-semibold mt-8 mb-3">4. Contact Us</h2>
          <p className="text-gray-600">
            If you have questions about this Privacy Policy, please contact us at{" "}
            <a href="/contact" className="text-indigo-600 hover:underline">
              our support page
            </a>.
          </p>
        </div>
      </div>
    </div>
  );
}
