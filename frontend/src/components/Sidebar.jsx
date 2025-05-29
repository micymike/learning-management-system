import React from 'react';
import { NavLink } from 'react-router-dom';
import { HiHome, HiClipboardCheck, HiUserGroup, HiChartBar, HiTrendingUp, HiChevronLeft } from 'react-icons/hi';

const Sidebar = ({ isOpen, onToggle }) => {
  const menuItems = [
    { path: '/', icon: HiHome, label: 'Dashboard' },
    { path: '/assessments', icon: HiClipboardCheck, label: 'Assessments' },
    { path: '/students', icon: HiUserGroup, label: 'Students' },
    { path: '/student-tracking', icon: HiTrendingUp, label: 'Student Tracking' },
    { path: '/analytics', icon: HiChartBar, label: 'Analytics' },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 h-full bg-white shadow-lg flex flex-col z-40 transition-all duration-300 ease-in-out 
        ${isOpen ? 'w-72' : 'w-20'}`}
      aria-label="Main navigation"
    >
      {/* Collapse Button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-6 bg-white rounded-full p-1.5 shadow-md text-gray-500 hover:text-green-600 transition-colors duration-200"
        aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        <HiChevronLeft className={`w-5 h-5 transition-transform duration-300 ${isOpen ? '' : 'rotate-180'}`} />
      </button>

      <div className="p-6 border-b border-gray-100">
        <h2 className={`text-2xl font-extrabold text-gray-800 tracking-tight mb-2 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
          {isOpen ? 'LMS Dashboard' : ''}
        </h2>
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
                title={!isOpen ? item.label : ''}
              >
                <item.icon className={`w-5 h-5 ${isOpen ? 'mr-3' : ''} transition-colors duration-200`} />
                <span className={`font-medium transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 w-0'}`}>
                  {isOpen ? item.label : ''}
                </span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className={`px-6 py-4 mt-auto border-t border-gray-100 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
        <span className="text-xs text-gray-400">v1.0.0</span>
      </div>
    </aside>
  );
};

export default Sidebar;
