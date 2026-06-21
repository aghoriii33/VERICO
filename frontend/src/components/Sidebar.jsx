import React from 'react';
import { LayoutDashboard, MessageSquare, BarChart3, ShieldCheck } from 'lucide-react';

export default function Sidebar({ currentTab, setCurrentTab }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chat', label: 'Compliance Chat', icon: MessageSquare },
    { id: 'analytics', label: 'Risk Analytics', icon: BarChart3 },
  ];

  return (
    <div className="sidebar">
      <div className="brand-section">
        <div className="brand-logo">
          <ShieldCheck size={22} color="white" />
        </div>
        <span className="brand-name">VERICO</span>
      </div>

      <nav className="nav-menu">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.id}
              className={`nav-item ${currentTab === item.id ? 'active' : ''}`}
              onClick={() => setCurrentTab(item.id)}
            >
              <Icon className="nav-icon" />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="user-avatar">CO</div>
        <div className="user-info">
          <h4>Compliance Officer</h4>
          <p>Risk & Legal Dept</p>
        </div>
      </div>
    </div>
  );
}
