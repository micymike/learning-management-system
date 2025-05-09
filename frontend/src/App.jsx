import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Dashboard from "./components/Dashboard";
import AssessmentWizard from "./components/AssessmentWizard";
import AssessmentDetails from "./components/AssessmentDetails";
import Sidebar from "./components/Sidebar";
import './index.css';

function AppWrapper() {
  const [darkMode, setDarkMode] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  // Check for user's preferred color scheme
  useEffect(() => {
    const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    setDarkMode(prefersDarkMode);
  }, []);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`bg-${darkMode ? 'black' : 'white'} min-h-screen`}>
      <div className="flex">
        <Sidebar />
        <div className="flex-1">
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route 
                path="/" 
                element={
                  <div className="page-transition">
                    <Dashboard onNewAssessment={() => navigate('/assessments/new')} onViewAssessment={(assessment) => navigate(`/assessments/${assessment.id}`)} />
                  </div>
                } 
              />
              <Route 
                path="/assessments" 
                element={
                  <div className="page-transition">
                    <Dashboard 
                      activeView="assessments"
                      onNewAssessment={() => navigate('/assessments/new')} 
                      onViewAssessment={(assessment) => navigate(`/assessments/${assessment.id}`)} 
                    />
                  </div>
                } 
              />
              <Route 
                path="/assessments/new" 
                element={
                  <div className="page-transition">
                    <AssessmentWizard onComplete={() => navigate('/')} onCancel={() => navigate('/')} />
                  </div>
                } 
              />
              <Route 
                path="/assessments/:id" 
                element={
                  <div className="page-transition">
                    <AssessmentDetails onBack={() => navigate('/')} />
                  </div>
                } 
              />
            </Routes>
          </AnimatePresence>
          {/* Dark Mode Toggle - using Tailwind classes */}
          <button 
            className="fixed bottom-6 right-6 p-3 bg-green-600 text-white rounded-full shadow-lg hover:bg-green-700 transition-colors focus:outline-none"
            onClick={toggleDarkMode}
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>

          {/* App Version */}
          <div className="fixed bottom-4 left-4 text-xs text-gray-500">v1.0.0</div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppWrapper />
    </Router>
  );
}

export default App;
