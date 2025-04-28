import React, { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Dashboard from "./components/Dashboard";
import AssessmentWizard from "./components/AssessmentWizard";
import AssessmentDetails from "./components/AssessmentDetails";
import './styles.css';

function App() {
  const [view, setView] = useState("dashboard");
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  // Check for user's preferred color scheme on initial load
  useEffect(() => {
    const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(prefersDarkMode);
    
    // Apply dark mode class if needed
    if (prefersDarkMode) {
      document.body.classList.add('dark-mode');
    }
  }, []);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  };

  const handleNewAssessment = () => {
    setView("wizard");
  };

  const handleWizardComplete = (results) => {
    setView("dashboard");
  };

  const handleViewAssessment = (assessment) => {
    setSelectedAssessment(assessment);
    setView("details");
  };

  const handleBackToDashboard = () => {
    setView("dashboard");
    setSelectedAssessment(null);
  };

  // Page transition variants
  const pageTransition = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3 }
  };

  return (
    <div className="app-container">
      <AnimatePresence mode="wait">
        {view === "dashboard" && (
          <motion.div
            key="dashboard"
            initial={pageTransition.initial}
            animate={pageTransition.animate}
            exit={pageTransition.exit}
            transition={pageTransition.transition}
            className="page-container"
          >
            <Dashboard 
              onNewAssessment={handleNewAssessment} 
              onViewAssessment={handleViewAssessment}
            />
          </motion.div>
        )}

        {view === "wizard" && (
          <motion.div
            key="wizard"
            initial={pageTransition.initial}
            animate={pageTransition.animate}
            exit={pageTransition.exit}
            transition={pageTransition.transition}
            className="page-container"
          >
            <AssessmentWizard 
              onComplete={handleWizardComplete} 
              onCancel={handleBackToDashboard}
            />
          </motion.div>
        )}

        {view === "details" && selectedAssessment && (
          <motion.div
            key="details"
            initial={pageTransition.initial}
            animate={pageTransition.animate}
            exit={pageTransition.exit}
            transition={pageTransition.transition}
            className="page-container"
          >
            <AssessmentDetails 
              assessment={selectedAssessment} 
              onBack={handleBackToDashboard}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Dark Mode Toggle */}
      <motion.button 
        className="dark-mode-toggle"
        onClick={toggleDarkMode}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        aria-label="Toggle dark mode"
      >
        {darkMode ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
          </svg>
        )}
      </motion.button>

      {/* App Version */}
      <div className="app-version">v1.0.0</div>
    </div>
  );
}

export default App;
