import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { HiHome, HiClipboardCheck, HiUserGroup, HiChartBar, HiTrendingUp } from 'react-icons/hi';

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

  const menuItems = [
    { path: '/', icon: HiHome, label: 'Dashboard' },
    { path: '/assessments', icon: HiClipboardCheck, label: 'Assessments' },
    { path: '/students', icon: HiUserGroup, label: 'Students' },
    { path: '/student-tracking', icon: HiTrendingUp, label: 'Student Tracking' },
    { path: '/analytics', icon: HiChartBar, label: 'Analytics' },
  ];

  const SidebarContent = () => (
    <>
      <div className="p-6 border-b border-gray-100">
        <h2 className="text-2xl font-extrabold text-gray-800 tracking-tight mb-2">LMS Dashboard</h2>
      </div>
      <nav className="py-6 flex-1">
        <ul className="space-y-1.5 px-3">
          {menuItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) => `
                  flex items-center px-4 py-3 rounded-xl transition-all duration-200
                  ${isActive 
                    ? 'bg-green-50 text-green-600 shadow-sm' 
                    : 'text-gray-600 hover:bg-gray-50 hover:text-green-600'
                  }
                `}
              >
                <item.icon className={`w-5 h-5 mr-3 transition-colors duration-200`} />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <div className="px-6 py-4 mt-auto border-t border-gray-100">
        <span className="text-xs text-gray-400">v1.0.0</span>
      </div>
    </>
  );

  if (isMobile) {
    return (
      <>
        <button
          className="fixed top-4 left-4 z-50 bg-white p-3 rounded-xl shadow-lg focus:outline-none hover:bg-gray-50 transition-colors duration-200"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation"
        >
          <div className="w-6 h-5 flex flex-col justify-between">
            <span className={`block h-0.5 bg-gray-600 rounded-full transition-all duration-300 ${menuOpen ? 'rotate-45 translate-y-2' : ''}`} />
            <span className={`block h-0.5 bg-gray-600 rounded-full transition-opacity duration-300 ${menuOpen ? 'opacity-0' : ''}`} />
            <span className={`block h-0.5 bg-gray-600 rounded-full transition-all duration-300 ${menuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
          </div>
        </button>
        <aside
          className={`
            fixed top-0 left-0 h-full w-72 bg-white shadow-xl flex flex-col z-40
            transform transition-transform duration-300 ease-in-out
            ${menuOpen ? 'translate-x-0' : '-translate-x-full'}
          `}
          aria-label="Main navigation"
        >
          <SidebarContent />
        </aside>
        {menuOpen && (
          <div
            className="fixed inset-0 bg-gray-800/20 backdrop-blur-sm z-30"
            onClick={() => setMenuOpen(false)}
            aria-hidden="true"
          />
        )}
      </>
    );
  }

  return (
    <aside
      className="fixed top-0 left-0 h-full w-72 bg-white shadow-lg flex flex-col z-40"
      aria-label="Main navigation"
    >
      <SidebarContent />
    </aside>
  );
};

export default Sidebar;
