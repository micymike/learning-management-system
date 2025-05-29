import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import Dashboard from "./components/Dashboard";
import AssessmentWizard from "./components/AssessmentWizard";
import AssessmentDetails from "./components/AssessmentDetails";
import Students from "./components/Students";
import StudentDetails from "./components/StudentDetails";
import StudentTracking from "./components/StudentTracking";
import Analytics from "./components/Analytics";
import Sidebar from "./components/Sidebar";
import './index.css';

function AppWrapper() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="bg-gradient-to-br from-gray-50 via-white to-gray-100 min-h-screen">
      <div className="flex">
        <Sidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
        <main className={`flex-1 p-10 md:p-16 transition-all duration-300 ${isSidebarOpen ? 'ml-72' : 'ml-20'}`}>
          <div className="max-w-5xl mx-auto bg-white rounded-3xl shadow-2xl p-10 min-h-[75vh] border border-gray-100">
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
                <Route 
                  path="/students" 
                  element={
                    <div className="page-transition">
                      <Students />
                    </div>
                  } 
                />
                <Route 
                  path="/students/:id" 
                  element={
                    <div className="page-transition">
                      <StudentDetails />
                    </div>
                  } 
                />
                <Route 
                  path="/student-tracking" 
                  element={
                    <div className="page-transition">
                      <StudentTracking />
                    </div>
                  } 
                />
                <Route 
                  path="/analytics" 
                  element={
                    <div className="page-transition">
                      <Analytics />
                    </div>
                  } 
                />
              </Routes>
            </AnimatePresence>
          </div>
        </main>
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
