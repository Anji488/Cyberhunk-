import { motion } from "framer-motion";
import { FaUserShield, FaExclamationTriangle, FaRobot } from "react-icons/fa";

export default function IntroductionBlock() {
  return (
    <section className="py-24 bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50">
      <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center md:items-start gap-16">

        <motion.div 
          className="md:w-1/2 flex justify-center md:justify-start"
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 1 }}
        >
          <img 
            src="/images/digital_responsibility.png" 
            alt="Digital Responsibility" 
            className="w-full max-w-md rounded-xl shadow-xl"
          />
        </motion.div>

        <motion.div 
          className="md:w-1/2 flex flex-col justify-center text-left space-y-6"
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 1 }}
        >
          <h2 className="text-3xl md:text-5xl font-extrabold text-indigo-900 mb-4">
            Why Digital Responsibility Matters
          </h2>
          <p className="text-lg md:text-xl text-gray-700">
            Social media connects over <strong>5.1 billion people worldwide</strong>. 
            But rising issues like cyberbullying, privacy leaks, misinformation, and mental health concerns make it essential to promote digital responsibility.
          </p>

          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <FaUserShield className="text-indigo-600 mt-1" size={24} />
              <span>
                <strong>Proactive Protection:</strong> CyberHunk helps you anticipate risks before they happen, rather than reacting afterward.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <FaExclamationTriangle className="text-yellow-500 mt-1" size={24} />
              <span>
                <strong>Awareness of Risks:</strong> Detect potential online hazards including cyberbullying, privacy threats, and misinformation.
              </span>
            </li>
            <li className="flex items-start gap-3">
              <FaRobot className="text-purple-600 mt-1" size={24} />
              <span>
                <strong>AI-Driven Guidance:</strong> CyberHunk uses advanced AI to guide responsible online behavior in real-time.
              </span>
            </li>
          </ul>
        </motion.div>

      </div>
    </section>
  );
}
