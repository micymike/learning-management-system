import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!isMobile) setMenuOpen(false);
  }, [isMobile]);

  if (isMobile) {
    return (
      <>
        <button
          className="fixed top-4 left-4 z-50 bg-primary text-white p-3 rounded-lg shadow-lg focus:outline-none"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          <span className="sr-only">Toggle navigation</span>
          <div className="w-6 h-6 flex flex-col justify-between">
            <span className="block h-1 bg-white rounded"></span>
            <span className="block h-1 bg-white rounded"></span>
            <span className="block h-1 bg-white rounded"></span>
          </div>
        </button>
        <aside
          className={`fixed top-0 left-0 h-full w-60 bg-white shadow-lg border-r border-gray-200 flex flex-col z-30 rounded-tr-2xl rounded-br-2xl transition-transform duration-300 ${menuOpen ? 'translate-x-0' : '-translate-x-full'}`}
          aria-label="Main navigation"
        >
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-2xl font-extrabold text-primary tracking-tight mb-2">Directed's LMS Dashboard</h2>
          </div>
          <ul className="py-6 flex-1 space-y-2">
            <li>
              <NavLink to="/" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-home" /></span> Dashboard </NavLink>
            </li>
            <li>
              <NavLink to="/assessments" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-tasks" /></span> Assessments </NavLink>
            </li>
            <li>
              <NavLink to="/students" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-user-graduate" /></span> Students </NavLink>
            </li>
            <li>
              <NavLink to="/student-tracking" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-chart-line" /></span> Student Tracking </NavLink>
            </li>
            <li>
              <NavLink to="/analytics" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-chart-bar" /></span> Analytics </NavLink>
            </li>
          </ul>
          <div className="px-6 py-4 mt-auto text-xs text-gray-400 border-t border-gray-100">v1.0.0</div>
        </aside>
      </>
    );
  }

  return (
    <aside
      className="fixed top-0 left-0 h-full w-60 bg-white shadow-lg border-r border-gray-200 flex flex-col z-30 rounded-tr-2xl rounded-br-2xl"
      aria-label="Main navigation"
    >
      <div className="p-6 border-b border-gray-100">
        <h2 className="text-2xl font-extrabold text-primary tracking-tight mb-2">LMS Dashboard</h2>
      </div>
      <ul className="py-6 flex-1 space-y-2">
        <li>
          <NavLink to="/" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-home" /></span> Dashboard </NavLink>
        </li>
        <li>
          <NavLink to="/assessments" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-tasks" /></span> Assessments </NavLink>
        </li>
        <li>
          <NavLink to="/students" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-user-graduate" /></span> Students </NavLink>
        </li>
        <li>
          <NavLink to="/student-tracking" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-chart-line" /></span> Student Tracking </NavLink>
        </li>
        <li>
          <NavLink to="/analytics" className={({ isActive }) => `flex items-center px-6 py-2 rounded-lg transition-colors duration-150 ${isActive ? 'bg-primary text-white shadow' : 'text-gray-700 hover:bg-gray-100'}`}> <span className="mr-3"><i className="fas fa-chart-bar" /></span> Analytics </NavLink>
        </li>
      </ul>
      <div className="px-6 py-4 mt-auto text-xs text-gray-400 border-t border-gray-100">v1.0.0</div>
    </aside>
  );
};

export default Sidebar;
