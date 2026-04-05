import React from 'react';
import { Outlet, useLocation, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, Home, ListTree, Receipt, Fingerprint, Shield, Users, User } from 'lucide-react';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home, roles: ['admin', 'analyst', 'viewer'] },
    { path: '/records', label: 'Financial Records', icon: Receipt, roles: ['admin', 'analyst'] },
    { path: '/events', label: 'Event Ledgers', icon: ListTree, roles: ['admin', 'analyst'] },
    { path: '/users', label: 'Club Members', icon: Users, roles: ['admin'] },
    { path: '/audit', label: 'Audit Trail', icon: Fingerprint, roles: ['admin', 'analyst'] },
  ];

  const visibleNav = navItems.filter(item => item.roles.includes(user?.role || ''));

  const roleBadge: Record<string, string> = {
    admin: 'bg-accent-purple/15 text-accent-purple border-accent-purple/20',
    analyst: 'bg-accent-blue/15 text-accent-blue border-accent-blue/20',
    viewer: 'bg-bg-card-hover text-text-secondary border-border-layer',
  };

  return (
    <div className="flex h-screen overflow-hidden bg-bg-primary text-text-primary font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-bg-card border-r border-border-layer flex flex-col p-6 shrink-0">
        <Link to="/dashboard" className="block mb-8">
          <h1 className="text-2xl font-bold tracking-tight">
            <Shield size={20} className="inline -mt-1 mr-1 text-accent-blue" />
            Vaultix<span className="text-accent-blue">.</span>
          </h1>
        </Link>

        <nav className="flex-1 space-y-1">
          {visibleNav.map((item) => {
            const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-accent-blue/10 text-accent-blue border-l-2 border-accent-blue'
                    : 'text-text-secondary hover:bg-bg-card-hover hover:text-text-primary'
                }`}
              >
                <item.icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto border-t border-border-layer pt-4 space-y-3">
          <Link to="/profile" className="block hover:bg-bg-card-hover rounded-lg p-2 -mx-2 transition-colors">
            <div className="text-sm font-semibold truncate">{user?.name}</div>
            <div className="text-xs text-text-secondary truncate">{user?.email}</div>
          </Link>
          <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded border inline-block ${roleBadge[user?.role || 'viewer']}`}>
            {user?.role}
          </span>
          {user?.assigned_event_id && (
            <div className="text-[10px] text-accent-yellow flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-yellow animate-pulse" />
              Event-Restricted View
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-text-secondary hover:text-accent-red transition-colors text-sm w-full mt-2"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto p-8 relative">
        <div className="fixed top-0 right-0 w-[50%] h-[50%] bg-accent-purple/5 rounded-full blur-[200px] pointer-events-none" />
        <div className="fixed bottom-0 left-[30%] w-[40%] h-[40%] bg-accent-blue/5 rounded-full blur-[200px] pointer-events-none" />
        <div className="max-w-7xl mx-auto relative z-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
