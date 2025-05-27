import React from 'react';
import { NavLink } from 'react-router-dom';
import { HiHome, HiClipboardCheck, HiUserGroup, HiChartBar, HiTrendingUp } from 'react-icons/hi';

const Sidebar = ({ isOpen }) => {
  const menuItems = [
    { path: '/', icon: HiHome, label: 'Dashboard' },
    { path: '/assessments', icon: HiClipboardCheck, label: 'Assessments' },
    { path: '/students', icon: HiUserGroup, label: 'Students' },
    { path: '/student-tracking', icon: HiTrendingUp, label: 'Student Tracking' },
    { path: '/analytics', icon: HiChartBar, label: 'Analytics' },
  ];

  return (
    <aside
      className={`fixed top-0 left-0 h-full bg-white shadow-lg flex flex-col z-40 transition-transform duration-300 ease-in-out ${isOpen ? 'w-72 translate-x-0' : 'w-0 translate-x-0'}`}
      aria-label="Main navigation"
    >
      <div className={`p-6 border-b border-gray-100 ${isOpen ? '' : 'hidden'}`}>
        <h2 className="text-2xl font-extrabold text-gray-800 tracking-tight mb-2">LMS Dashboard</h2>
      </div>
      <nav className={`py-6 flex-1 ${isOpen ? '' : 'hidden'}`}>
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
      <div className={`px-6 py-4 mt-auto border-t border-gray-100 ${isOpen ? '' : 'hidden'}`}>
        <span className="text-xs text-gray-400">v1.0.0</span>
      </div>
    </aside>
  );
};

export default Sidebar;
