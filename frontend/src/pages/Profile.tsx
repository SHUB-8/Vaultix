import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, Mail, Calendar, Layers } from 'lucide-react';

export default function Profile() {
  const { user } = useAuth();
  if (!user) return null;

  const roleBadge: Record<string, string> = {
    admin: 'bg-accent-purple/15 text-accent-purple border-accent-purple/20',
    analyst: 'bg-accent-blue/15 text-accent-blue border-accent-blue/20',
    viewer: 'bg-bg-card-hover text-text-secondary border-border-layer',
  };

  return (
    <div className="max-w-lg mx-auto">
      <h1 className="text-3xl font-bold tracking-tight mb-6">My Profile</h1>

      <div className="glass-card p-8 space-y-6">
        <div className="w-16 h-16 rounded-full bg-accent-blue/15 flex items-center justify-center text-accent-blue text-2xl font-bold">
          {user.name.charAt(0).toUpperCase()}
        </div>

        <div className="space-y-4">
          <div>
            <div className="text-xs uppercase tracking-widest text-text-secondary font-semibold mb-1">Full Name</div>
            <div className="text-lg font-semibold">{user.name}</div>
          </div>

          <div className="flex items-center gap-2">
            <Mail size={14} className="text-text-secondary" />
            <span className="text-text-secondary text-sm font-mono">{user.email}</span>
          </div>

          <div className="flex items-center gap-2">
            <Shield size={14} className="text-text-secondary" />
            <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider border ${roleBadge[user.role]}`}>
              {user.role}
            </span>
          </div>

          {user.assigned_event_id && (
            <div className="flex items-center gap-2 text-accent-yellow text-sm">
              <Layers size={14} />
              <span>Event-restricted access</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
