import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Sidebar = ({ activeView }) => {
  const [isMobile, setIsMobile] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) setMenuOpen(true);
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleMenu = () => setMenuOpen(!menuOpen);

  return (
    <>
      {isMobile && (
        <button 
          className="fixed top-4 left-4 z-50 bg-green-600 p-2 rounded-md focus:outline-none"
          onClick={toggleMenu}
          aria-expanded={menuOpen}
          aria-label="Toggle menu"
        >
          <div className={`flex flex-col justify-between h-6 w-6`}>  
            <span className={`block h-0.5 w-full bg-white transition-transform duration-300 ${menuOpen ? 'rotate-45 translate-y-2.5' : ''}`}></span>
            <span className={`block h-0.5 w-full bg-white transition-opacity duration-300 ${menuOpen ? 'opacity-0' : 'opacity-100'}`}></span>
            <span className={`block h-0.5 w-full bg-white transition-transform duration-300 ${menuOpen ? '-rotate-45 -translate-y-2.5' : ''}`}></span>
          </div>
        </button>
      )}
      <nav 
        className={`fixed top-0 left-0 h-full w-64 bg-white shadow-lg z-40 transform transition-transform duration-300 ease-in-out ${
          menuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
        aria-label="Main navigation"
      >
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-black">LMS Dashboard</h2>
        </div>
        <ul className="py-4">
          <li className="mb-1">
            <Link 
              to="/" 
              className={`flex items-center px-6 py-3 text-gray-800 hover:bg-gray-100 ${
                activeView === 'dashboard' ? 'bg-gray-100 border-l-4 border-green-600 font-medium' : ''
              }`}
              aria-current={activeView === 'dashboard' ? 'page' : undefined}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Dashboard
            </Link>
          </li>
          <li className="mb-1">
            <Link 
              to="/assessments" 
              className={`flex items-center px-6 py-3 text-gray-800 hover:bg-gray-100 ${
                activeView === 'assessments' ? 'bg-gray-100 border-l-4 border-green-600 font-medium' : ''
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Assessments
            </Link>
          </li>
          <li className="mb-1">
            <Link 
              to="/students" 
              className={`flex items-center px-6 py-3 text-gray-800 hover:bg-gray-100 ${
                activeView === 'students' ? 'bg-gray-100 border-l-4 border-green-600 font-medium' : ''
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              Students
            </Link>
          </li>
          <li className="mb-1">
            <Link 
              to="/analytics" 
              className={`flex items-center px-6 py-3 text-gray-800 hover:bg-gray-100 ${
                activeView === 'analytics' ? 'bg-gray-100 border-l-4 border-green-600 font-medium' : ''
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Analytics
            </Link>
          </li>
        </ul>
      </nav>
    </>
  );
};

export default Sidebar;
